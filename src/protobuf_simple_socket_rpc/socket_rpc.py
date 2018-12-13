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

from google.protobuf.message import Message


class SocketRPC(socket.socket):
    '''
    simple socket rpc implementation for protobuf
    '''

    def __init__(self, *args: int, **kwargs: int) -> None:
        '''
        class init method
        :param args: args which will be passed to socket constructor directly
        :param kwargs: kwargs which will be passed to socket constructor directly
        '''
        socket.socket.__init__(self, *args, **kwargs)

    def __recv(self, size: int) -> bytes:
        '''
        method to receive exact size bytes from server
        :param size: server response size in bytes
        :throw RuntimeError: in case if socket was closed before chunk was read
        :return: server response
        '''
        buffer = b''
        while size > 0:
            chunk = self.recv(size)
            if not chunk:
                raise RuntimeError('connection closed before chunk was read')
            buffer += chunk
            size -= len(chunk)
        return buffer

    def handshake(self, client_response: bytes,
                  server_response: bytes) -> bool:
        '''
        perform handshake with remote server
        :param client_response: client string to be passed to server
        :param server_response: server response expected on connection
        :return: true in case of successfully handshake
        '''
        response = self.__recv(len(server_response))
        if response != server_response:
            return False
        self.sendall(client_response)
        return True

    def read_message(self, message: Message) -> Message:
        '''
        read response from server and serialize it to message
        :param message: empty message to serialize to
        :return: serialized protobuf message
        '''
        message_len_buffer = self.__recv(
            4)  # message size is (always?) 4 bytes
        (message_len,) = struct.unpack('>I', message_len_buffer)

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