from flask import Flask

import mock

from flask_zmq import ZMQ


def test_call():

    app = Flask(__name__)
    app.config.update(
        ZMQ_HANDLERS={
            'call': {'address': 'ipc:///tmp/flask-zmq-test.sock'},
        },
    )

    @app.route('/call')
    def view():
        call('foo', bar='baz')
        return 'OK'

    zmq = ZMQ()

    call_mock = mock.Mock(__name__='call', side_effect=KeyboardInterrupt())
    call = zmq.handler(call_mock)

    with app.app_context():
        call.bind()

    resp = app.test_client().get('/call')
    assert resp.data.decode(resp.charset) == 'OK'

    with app.app_context():
        call.serve()

    assert call_mock.call_args == mock.call('foo', bar='baz')
