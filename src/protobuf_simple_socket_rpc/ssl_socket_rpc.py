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


import ssl

from protobuf_simple_socket_rpc.socket_rpc import SocketRPC


class SSLSocketRPC(SocketRPC, ssl.SSLSocket):
    '''
    socket rpc with ssl support

    In order to use it just assign SSLContext.sslsocket_class value
    '''

    def __init__(self, *args: int, **kwargs: int) -> None:
        '''
        class init method
        :param args: args which will be passed to socket constructor directly
        :param kwargs: kwargs which will be passed to socket constructor directly
        '''
        SocketRPC.__init__(self, *args, **kwargs)
