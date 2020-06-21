import struct
import asyncio
from asyncio import StreamReader, StreamWriter


@asyncio.coroutine
def handle_echo(reader: StreamReader,
                writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print("Connect from %r" % (addr,))

    count = 0

    try:
        with open('data.dat', 'wb') as fout:
            while True:
                data = yield from reader.readexactly(4)
                user_id, body_len = struct.unpack("!HH", data)
                data = yield from reader.readexactly(body_len)
                fout.write(data)

                if count % 100 == 0:
                    msg = '안녕하세요.'
                    msg_encoded = str.encode(msg)
                    header = struct.pack("!HH", user_id, len(msg_encoded))
                    writer.write(header + msg_encoded)
                    yield from writer.drain()

                count += 1
    except Exception as e:
        print(e)
        writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
