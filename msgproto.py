import asyncio

# Здесь простенький протокол, который отправляет в начале сообщения его размер.
# Ну а чтение идет именно того размера который получил.

SEPARATOR = ',-;'


async def read_msg(stream: asyncio.StreamReader) -> bytes:
    try:
        size_bytes = await stream.readexactly(4)
        size = int.from_bytes(size_bytes, byteorder='big')
        data = await stream.readexactly(size)
        return data
    except asyncio.IncompleteReadError as e:
        raise StopIteration(e.args)


async def send_msg(stream: asyncio.StreamWriter, data: bytes):
    size_bytes = len(data).to_bytes(4, byteorder='big')
    stream.writelines([size_bytes, data])
    await stream.drain()
