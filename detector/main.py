import io
import wave
import struct
import asyncio
from asyncio import StreamReader, StreamWriter

import numpy as np

from label_wav import load_labels, load_graph, run_graph


def convert_pcm_to_wav(pcm: bytes) -> bytes:
    np_array_float32: np.ndarray = np.frombuffer(pcm, dtype=np.float32) * 32768
    np_array_int16 = np_array_float32.astype(np.int16)

    buffer = io.BytesIO()

    with wave.open(buffer, 'wb') as fout:
        fout.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        fout.writeframes(np_array_int16.tobytes())

    return buffer.getvalue()


@asyncio.coroutine
def handle_echo(reader: StreamReader,
                writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print("Connect from %r" % (addr,))
    labels_list = load_labels('labels/labels.txt')
    load_graph('model/my_frozen_graph_okyonsei.pb')

    count = 0
    last_data = dict()

    try:
        while True:
            data = yield from reader.readexactly(8)
            user_id, body_len = struct.unpack("!II", data)
            data = yield from reader.readexactly(body_len)
            wav_data = convert_pcm_to_wav(data)

            with open(f'{count}.wav', 'wb') as fout:
                fout.write(wav_data)

            run_graph(wav_data, labels_list, 3)

            if count % 100 == 0:
                msg = f'안녕하세요. {count}'
                msg_encoded = str.encode(msg)
                header = struct.pack("!II", user_id, len(msg_encoded))
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
