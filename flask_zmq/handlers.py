from functools import update_wrapper
import logging

import zmq

import click

from flask import current_app


class NotConfigured(click.ClickException):
    def __init__(self, handler):
        super().__init__("ZMQ_HANDLERS['%s'] is not configured" % handler)


class ZMQHandler(object):

    def __init__(self, handler, zmq):
        update_wrapper(self, handler)
        self.handler = handler
        self.zmq = zmq
        self.socket = None
        self.server_socket = None

    def __call__(self, *args, **kwargs):
        if self.socket is None:
            self.connect()
        self.send(*args, **kwargs)

    def connect(self, address=None):

        cfg = current_app.config['ZMQ_HANDLERS'].get(self.__name__)
        if cfg is None:
            raise NotConfigured(self.__name__)

        if address is None:
            address = cfg['address']

        self.socket = self.zmq.ctx.socket(zmq.PUSH)
        self.socket.connect(address)

    def bind(self, bind_address=None):

        cfg = current_app.config['ZMQ_HANDLERS'].get(self.__name__)
        if cfg is None:
            raise NotConfigured(self.__name__)

        if bind_address is None:
            bind_address = cfg['address']

        self.server_socket = self.zmq.ctx.socket(zmq.PULL)
        self.server_socket.bind(bind_address)

    def serve(self, bind_address=None):

        if self.server_socket is None:
            self.bind(bind_address)

        while True:
            try:
                self.handle()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error("%s failed with %s", self.__name__, e,
                              exc_info=True)

        logging.info("Stopping")

    def send(self, *args, **kwargs):
        self.socket.send_pyobj(args, zmq.SNDMORE)
        self.socket.send_pyobj(kwargs)

    def handle(self):
        args = self.server_socket.recv_pyobj()
        kwargs = self.server_socket.recv_pyobj()
        self.handler(*args, **kwargs)


class CrosslangZMQHandler(ZMQHandler):
    def send(self, *args):
        self.socket.send_multipart(args)

    def handle(self):
        args = self.server_socket.recv_multipart()
        self.handler(*args)
