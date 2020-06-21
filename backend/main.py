import struct
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from weakref import WeakValueDictionary

from aiohttp import web, WSCloseCode, WSMsgType, WSMessage

import exceptions

NUM_SERVICE = 1


async def listen_to_detector(app):
    reader: StreamReader = app['reader']
    ws_dict: WeakValueDictionary = app['web_sockets']['ws']
    try:
        while True:
            data = await reader.readexactly(4)
            user_id, body_len = struct.unpack("!HH", data)
            data = await reader.readexactly(body_len)
            msg = data.decode()
            ws: web.WebSocketResponse = ws_dict.get(user_id)

            if ws is None:
                continue
            await ws.send_json({'msg': msg})
    except Exception as e:
        logging.error(e)


async def start_background_tasks(app):
    app['detector_listener'] = asyncio.create_task(listen_to_detector(app))


async def cleanup_background_tasks(app):
    app['detector_listener'].cancel()
    await app['detector_listener']


async def on_shutdown(app):
    for ws in app['web_sockets']['ws'].valuerefs():
        await ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown')


async def handle_keyword_spotting(request):
    ws = web.WebSocketResponse()
    user_id = -1

    try:
        await ws.prepare(request)
        logging.info(f'Connected from {request.headers.get("Origin", "Unknown")}')
        ws_dict: WeakValueDictionary = request.app['web_sockets']['ws']

        if len(ws_dict) >= NUM_SERVICE:
            raise exceptions.ServiceFullException

        user_id = request.app['web_sockets']['num']
        request.app['web_sockets']['num'] += 1
        ws_dict[user_id] = ws
        writer: StreamWriter = request.app['writer']

        with open('data.dat', 'wb') as fout:
            msg: WSMessage
            async for msg in ws:
                if msg.type == WSMsgType.BINARY:
                    fout.write(msg.data)
                    header = struct.pack("!HH", user_id, len(msg.data))
                    writer.write(header + msg.data)
                    await writer.drain()

    except exceptions.ServiceFullException:
        await ws.close(code=WSCloseCode.POLICY_VIOLATION,
                       message=b'service full')
    except Exception:
        await ws.close(code=WSCloseCode.INTERNAL_ERROR,
                       message=b'error')
    finally:
        ws_dict.pop(user_id, None)
    return ws


async def web_app():
    app = web.Application()
    app['web_sockets'] = {
        'ws': WeakValueDictionary(),
        'num': 0,
    }

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    app['reader'] = reader
    app['writer'] = writer

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(on_shutdown)
    app.add_routes([
        web.get('/ws/keyword-spotting', handle_keyword_spotting),
    ])

    return app


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )

    app = web_app()
    web.run_app(app)
