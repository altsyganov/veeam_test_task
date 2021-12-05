import asyncio
import argparse
import logging

from msgproto import read_msg, send_msg, SEPARATOR


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)


class Client:

    def __init__(self, login):
        self.login = login
        self.token = None

    async def auth_on_server(self) -> None:
        try:
            addr = ('127.0.0.1', 8000)
            reader, writer = await asyncio.open_connection(*addr)


            await send_msg(writer, self.login.encode())
            logging.debug(f'Sent {self.login!r} to {addr}')

            response = await read_msg(reader)
            token = response.decode()
            logging.debug(f'Received response from {addr}: {token!r}')
            self.token = token

            logging.debug(f'Close the connection with {addr}')
        except StopIteration:
            logging.debug(f'{addr} disconnected')
        finally:
            writer.close()


    async def send_message(self, message) -> None:
        try:
            addr = ('127.0.0.1', 8001)
            reader, writer = await asyncio.open_connection(*addr)
            msg = str(input())
            data = f"{message}{SEPARATOR}{self.token}{SEPARATOR}{self.login}"
            await send_msg(writer, data.encode())
            logging.debug(f'Sent {data!r} to {addr}')

            response = await read_msg(reader)
            logging.debug(f'Received response from {addr}: {response.decode()!r}')
        finally:
            writer.close()



if __name__ == '__main__':
    try:
        while True:
            correct_input = False
            while not correct_input:
                login = str(input('Enter your login: '))
                if SEPARATOR in login:
                    print(f'Please remove {SEPARATOR!r} from login')
                else:
                    correct_input = True
            client = Client(login)
            asyncio.run(client.auth_on_server())
            message = str(input('Enter message to log on server: '))
            asyncio.run(client.send_message(message))
    except KeyboardInterrupt:
        logging.debug('Connections closed, bye.')
