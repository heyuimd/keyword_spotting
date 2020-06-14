import asyncio
from aiohttp import web, WSCloseCode, WSMsgType, WSMessage
import logging
import weakref
import exceptions

NUM_SERVICE = 2


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


async def handle_keyword_spotting(request):
    ws = web.WebSocketResponse()
    i = 0

    try:
        app_ws = request.app['websockets']
        await ws.prepare(request)
        logging.info(f'in from {request.headers.get("Origin", "Unknown")}')
        app_ws.add(ws)

        if len(app_ws) > NUM_SERVICE:
            raise exceptions.ServiceFullException

        msg: WSMessage
        async for msg in ws:
            if msg.type in (WSMsgType.TEXT, WSMsgType.BINARY):
                i += 1

            if i % 100 == 0:
                logging.info(i)
                await ws.send_json({'msg': f'sending {i}'})

    except exceptions.ServiceFullException:
        await ws.close(code=WSCloseCode.POLICY_VIOLATION,
                       message=b'service full')
    except Exception:
        await ws.close(code=WSCloseCode.INTERNAL_ERROR,
                       message=b'error')
    finally:
        app_ws.discard(ws)

    return ws


async def web_app():
    app = web.Application()
    app['websockets'] = weakref.WeakSet()

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
