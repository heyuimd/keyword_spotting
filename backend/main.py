import struct
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from weakref import WeakValueDictionary

from aiohttp import web, WSCloseCode, WSMsgType, WSMessage

import exceptions

NUM_SERVICE = 2


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
