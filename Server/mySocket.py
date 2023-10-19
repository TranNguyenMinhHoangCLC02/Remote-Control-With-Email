import socket
import struct
import threading
import pickle

CHUNKSIZE = 4096
SIZE_LEN = 8

class MySocket(socket.socket):
    def __init__(self, *args, **kwargs):
        super(MySocket, self).__init__(*args, **kwargs)
        self.__block = threading.Lock()
        self.__client = None

    def close(self) -> None:
        with self.__block:
            res = super().close()
        return res

    def accept(self):
        self.__client, addr = super().accept()
        return self, addr


    def send(self, __data) -> int:
        with self.__block:
            size = struct.pack(">Q", len(__data))
            self.__client.sendall(size)
            res = self.__client.sendall(__data)
        return res

    def recv(self, __bufsize: int) -> bytes:
        with self.__block:
            (size, ) = struct.unpack(">Q", self.__client.recv(SIZE_LEN))
            res = bytearray()
            while size > 0:
                chunk = min(size, CHUNKSIZE)
                res += self.__client.recv(chunk)
                size -= chunk
        return res

