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
        self.socket.send_pyobj(args, zmq.SNDMORE)
        self.socket.send_pyobj(kwargs)

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

        try:
            while True:
                args = self.server_socket.recv_pyobj()
                kwargs = self.server_socket.recv_pyobj()
                try:
                    self.handler(*args, **kwargs)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error("%s(*%s, **%s) failed with %s",
                                  self.__name__, args, kwargs, e,
                                  exc_info=True)
        except KeyboardInterrupt:
            pass

        logging.info("Stopping")
