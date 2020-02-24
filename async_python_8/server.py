import asyncio
import functools
import json
import warnings
from typing import Dict, Any, Union, Optional

import aioredis
import trio
import trio_asyncio
from aioredis import Redis
from hypercorn.trio import serve
from hypercorn.config import Config as HyperConfig
from werkzeug.datastructures import MultiDict

from quart_trio import QuartTrio
from quart import request, websocket, Response

from async_python_8 import smsc, utils
from async_python_8 import db


class ExtendedQuartTrio(QuartTrio):
    """subclassing used cuz mypy doesn't like dynamic attributes"""
    db: db.Database
    redis: Optional[Redis] = None


app = ExtendedQuartTrio(__name__)


@app.before_serving
async def init_db() -> None:
    # TODO: use connection string from env
    redis_connection_string = "redis://127.0.0.1:6379"
    create_redis_pool = functools.partial(
        aioredis.create_redis_pool, encoding='utf-8')
    app.redis = await trio_asyncio.run_asyncio(
        create_redis_pool, redis_connection_string)
    app.db = db.Database(app.redis)


@app.after_serving
async def close_redis() -> None:
    if app.redis is not None:
        app.redis.close()
        await trio_asyncio.run_asyncio(app.redis.wait_closed)


@app.route("/", methods=["GET", ])
async def index() -> Response:
    return await app.send_static_file("index.html")


@app.route('/send/', methods=['POST'])
async def create_mailing() -> Dict:
    form: MultiDict = await request.form
    try:
        text: str = form["text"]
        mailing_id = await trio_asyncio.run_asyncio(app.db.get_mailing_id)
        phones_list = ["+79305551234", "911", "112"]
        await trio_asyncio.run_asyncio(
            app.db.add_sms_mailing, mailing_id, phones_list, text)
    except smsc.SMSCApiError as e:
        msg = f"something went wrong: {str(e)}"
        return {"errorMessage": msg}
    else:
        return {}


@app.websocket("/ws")
async def ws() -> None:
    # FIXME: handler doesn't understand when tab in browser is closed
    while True:
        sms_ids = await trio_asyncio.run_asyncio(
            app.db.list_sms_mailings)
        print('Registered mailings ids', sms_ids)
        mailings_list = await trio_asyncio.run_asyncio(
            app.db.get_sms_mailings, *sms_ids)
        response = {
            "msgType": "SMSMailingStatus",
            "SMSMailings": [
                utils.convert_mailing_info(x) for x in mailings_list
            ]
        }
        await websocket.send(json.dumps(response))
        await trio.sleep(1)


async def run_server() -> None:
    async with trio_asyncio.open_loop():
        asyncio._set_running_loop(asyncio.get_event_loop())  # noqa
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)


def main():
    warnings.filterwarnings("ignore", category=trio.TrioDeprecationWarning)
    trio.run(run_server)


if __name__ == "__main__":
    main()
