import asyncio
import datetime
import logging
from hashlib import sha1

from msgproto import read_msg, send_msg, SEPARATOR


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(filename='veeam_cli_serv.log')
file_handler.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=(console_handler, file_handler),
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)


class Server:

    UNAUTHORIZED_MSG = 'Token {} is not valid for user {}'
    INCORRECT_MSG_FORMAT = 'Given msg is not valid'
    SUCCESS_MESSAGE = 'All went good, message logged'

    def __init__(self) -> None:
        self.clients = {}

    async def handle_auth(self, reader: asyncio.StreamReader,
                          writer: asyncio.StreamWriter) -> None:
        try:
            addr = writer.get_extra_info('peername')
            data = await read_msg(reader)
            user_uid = data.decode()
            logging.debug(f'Received {user_uid!r} from {addr}')

            salt = f'{addr} + {datetime.datetime.now()}'
            hash = sha1(f'{user_uid} {salt}'.encode()).hexdigest()
            logging.debug(
                f'Computed key for {user_uid} from {addr} is {hash!r}'
            )

            self.clients[hash] = user_uid

            await send_msg(writer, hash.encode())

            logging.debug(f'Close the connection with {addr}')
        except RuntimeError:
            logging.debug(f'error {addr} disconnected')
        finally:
            writer.close()

    async def handle_message(self, reader: asyncio.StreamReader,
                             writer: asyncio.StreamWriter) -> None:
        try:
            addr = writer.get_extra_info('peername')
            data = await read_msg(reader)
            try:
                user_message, hash, login = data.decode().split(maxsplit=2,
                                                                sep=SEPARATOR)
                response_data = self.SUCCESS_MESSAGE
                logging.debug(f'Received {data.decode()!r} from {addr}')
                if self.clients.get(hash) == login:
                    logging.debug(f'{login} from {addr} authorized')
                    # Здесь записывает полученное сообщение в лог-файл
                    logging.info(f"{login} from {addr} sent {user_message}")
                    self.clients.pop(hash)
                else:
                    logging.debug(
                        f'{login} from {addr} provided invalid token'
                    )
                    response_data = self.UNAUTHORIZED_MSG.format(hash, login)
            except ValueError:
                logging.debug(f'{addr} sent invalid message')
                response_data = self.INCORRECT_MSG_FORMAT
            await send_msg(writer, response_data.encode())
        except RuntimeError:
            logging.debug(f'{addr} disconnected')
        finally:
            writer.close()


async def main():

    server = Server()

    auth_server = await asyncio.start_server(
        server.handle_auth,
        '127.0.0.1',
        8000
    )

    message_server = await asyncio.start_server(
        server.handle_message,
        '127.0.0.1',
        8001
    )

    async with auth_server:
        await auth_server.serve_forever()

    async with message_server:
        await message_server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.debug('Connections closed, server down')
