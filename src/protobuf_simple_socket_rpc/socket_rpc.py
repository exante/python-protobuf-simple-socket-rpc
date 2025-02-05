##########################################################################
# Copyright (c) 2018 EXANTE                                                     #
#                                                                               #
# Permission is hereby granted, free of charge, to any person obtaining a copy  #
# of this software and associated documentation files (the "Software"), to deal #
# in the Software without restriction, including without limitation the rights  #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     #
# copies of the Software, and to permit persons to whom the Software is         #
# furnished to do so, subject to the following conditions:                      #
#                                                                               #
# The above copyright notice and this permission notice shall be included in    #
# all copies or substantial portions of the Software.                           #
##########################################################################


import socket
import struct

from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.message import Message


class SocketRPC(socket.socket):
    '''
    simple socket rpc implementation for protobuf
    '''

    # unconsumed buffer from __recv
    # this property is not initialized in __init__ because ssl.SSLSocket doesn't have
    # (adn doesn't call) __init__ method
    _buffer: bytes = b''

    def __recv(self, size: int) -> bytes:
        '''
        method to receive exact size bytes from server
        :param size: server response size in bytes
        :return: server response
        '''
        # copy bytes from unconsumed buffer if available
        buffer, self._buffer = self._buffer[:size], self._buffer[size:]
        size -= len(buffer)

        while size > 0:
            chunk = self.recv(1)
            if len(chunk) > size:  # if read size exceeds the requested, then save remaining bytes in buffer
                chunk, self._buffer = chunk[:size], chunk[size:]
            buffer += chunk
            size -= len(chunk)

        return buffer

    def _read_varint(self) -> int:
        '''
        credits to https://github.com/soulmachine/delimited-protobuf/blob/main/delimited_protobuf.py
        read varint message size from socket
        :return: message size in bytes
        '''
        buffer = self.__recv(1)
        if not buffer:
            return 0

        while (buffer[-1] & 0x80) >> 7 == 1:  # while the MSB is 1
            chunk = self.__recv(1)
            if not chunk:
                raise EOFError('unexpected EOF')
            buffer += chunk

        varint, _ = _DecodeVarint(buffer, 0)
        return varint

    def handshake_client(self, client_response: bytes,
                         server_response: bytes) -> bool:
        '''
        perform handshake with remote server (client initiated)
        :param client_response: client string to be passed to server
        :param server_response: server response expected on connection
        :return: true in case of successfully handshake
        '''
        self.sendall(client_response)
        return self.__recv(len(server_response)) == server_response

    def handshake_server(self, client_response: bytes,
                         server_response: bytes) -> bool:
        '''
        perform handshake with remote server (server initiated)
        :param client_response: client string to be passed to server
        :param server_response: server response expected on connection
        :return: true in case of successfully handshake
        '''
        response = self.__recv(len(server_response))
        if response != server_response:
            return False
        self.sendall(client_response)
        return True

    def read_message(self, message: Message, message_len_struct: str | None = 'I') -> Message:
        '''
        read response from server and serialize it to message
        :param message: empty message to serialize to
        :param message_len_struct: message len struct, default I
        :return: serialized protobuf message
        '''
        if message_len_struct is None:
            message_len = self._read_varint()
        else:
            message_len_buffer_size = struct.Struct(message_len_struct).size
            message_len_buffer = self.__recv(message_len_buffer_size)
            (message_len,) = struct.unpack('>' + message_len_struct, message_len_buffer)

        message.ParseFromString(self.__recv(message_len))

        return message

    def send_message(self, message: Message) -> None:
        '''
        send protobuf message to server
        :param message: protobuf message
        '''
        packed_len = struct.pack('>I', message.ByteSize())
        self.sendall(packed_len)
        self.sendall(message.SerializeToString())
