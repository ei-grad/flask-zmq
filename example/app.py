import json
import os
import sqlite3

from flask import Flask, g, request, render_template

from flask_zmq import ZMQ


app = Flask(__name__)
app.config.update(
    WORK_DIR='.',
    ZMQ_HANDLERS={
        'call': {
            'address': 'ipc://./call.sock'
        },
    },
)

zmq = ZMQ(app)


@app.route('/')
def index():
    return render_template('index.html')


def connect_db():
    return sqlite3.connect(os.path.join(app.config['WORK_DIR'], 'example.db'))


@app.cli.command()
def create_db():
    db = connect_db()
    db.execute('''
    CREATE TABLE calls (
        args TEXT,
        kwargs TEXT
    );
    ''')
    db.commit()
    db.close()


@app.before_request
def open_db():
    g.db = connect_db()


@app.after_request
def close_db(response):
    g.db.close()
    return response


@app.route('/call')
def call_view():
    args = json.loads(request.args['args'])
    kwargs = json.loads(request.args['kwargs'])
    call(*args, **kwargs)
    return 'OK'


@zmq.handler('call')
def call(*args, **kwargs):
    db = connect_db()
    db.execute('insert into calls (args, kwargs) values (?, ?)',
               [json.dumps(args), json.dumps(kwargs)])
    db.commit()
