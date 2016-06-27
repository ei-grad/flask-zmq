from functools import wraps

import click

from flask import _app_ctx_stack as stack

import zmq

from flask_zmq.handlers import ZMQHandler


class ZMQ(object):

    def __init__(self, app=None):
        self._delayed = []
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        for command_name, zmq_server in self._delayed:
            app.cli.command(command_name)(zmq_server)

    @property
    def ctx(self):
        top = stack.top
        if top is not None:
            if not hasattr(top, 'zmq_ctx'):
                top.zmq_ctx = zmq.Context()
            return top.zmq_ctx

    def handler(self, handler_or_command_name):

        def decorator(handler):

            @click.option('--bind-address')
            @wraps(handler)
            def zmq_server(bind_address):
                return zmq_handler.serve(bind_address)

            zmq_handler = ZMQHandler(handler, self)

            zmq_server.__doc__ = "Start server for %s." % command_name

            if self.app is not None:
                self.app.cli.command(command_name)(zmq_server)
            else:
                self._delayed.append((command_name, zmq_server))

            return zmq_handler

        if callable(handler_or_command_name):
            handler = handler_or_command_name
            command_name = handler.__name__
            return decorator(handler)
        else:
            command_name = handler_or_command_name
            return decorator
