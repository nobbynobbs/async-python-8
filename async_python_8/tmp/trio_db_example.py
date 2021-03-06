import asyncio
import argparse
import functools
import warnings

import aioredis
import trio
import trio_asyncio
from trio import TrioDeprecationWarning

from async_python_8.db import Database

warnings.filterwarnings("ignore", category=TrioDeprecationWarning)


def create_argparser():
    parser = argparse.ArgumentParser(
        description='Redis database usage example')
    parser.add_argument(
        '--address',
        action='store',
        dest='redis_uri',
        help='Redis URI',
        default="redis://127.0.0.1:6379")

    return parser


async def main():
    asyncio._set_running_loop(asyncio.get_event_loop())  # noqa

    parser = create_argparser()
    args = parser.parse_args()

    create_redis_pool = functools.partial(
        aioredis.create_redis_pool, encoding='utf-8')
    redis = await trio_asyncio.run_asyncio(create_redis_pool, args.redis_uri)

    try:

        db = Database(redis)

        sms_id = '1'

        phones = [
            '+7 999 519 05 57',
            '911',
            '112',
        ]
        text = 'Вечером будет шторм!'

        await trio_asyncio.run_asyncio(
            db.add_sms_mailing, sms_id, phones, text)

        sms_ids = await trio_asyncio.run_asyncio(
            db.list_sms_mailings)
        print('Registered mailings ids', sms_ids)

        pending_sms_list = await trio_asyncio.run_asyncio(
            db.get_pending_sms_list())
        print('pending:')
        print(pending_sms_list)

        await trio_asyncio.run_asyncio(db.update_sms_status_in_bulk, [
            # [sms_id, phone_number, status]
            [sms_id, '112', 'failed'],
            [sms_id, '911', 'pending'],
            [sms_id, '+7 999 519 05 57', 'delivered'],
            # following statuses are available: failed, pending, delivered
        ])

        pending_sms_list = await trio_asyncio.run_asyncio(
            db.get_pending_sms_list)
        print('pending:')
        print(pending_sms_list)

        sms_mailings = await trio_asyncio.run_asyncio(
            db.get_sms_mailings, '1')
        print('sms_mailings')
        print(sms_mailings)

        async def send():
            while True:
                await trio.sleep(1)
                await trio_asyncio.run_asyncio(
                    redis.publish, 'updates', sms_id)

        async def listen():
            *_, channel = await trio_asyncio.run_asyncio(
                redis.subscribe, 'updates')

            while True:
                raw_message = await trio_asyncio.run_asyncio(channel.get)

                if not raw_message:
                    raise ConnectionError('Connection was lost')

                message = raw_message.decode('utf-8')
                print('Got message:', message)

        async with trio.open_nursery() as nursery:
            nursery.start_soon(send)
            nursery.start_soon(listen)

    finally:
        redis.close()
        await trio_asyncio.run_asyncio(redis.wait_closed)


if __name__ == '__main__':
    trio_asyncio.run(main)
