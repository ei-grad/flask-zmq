from setuptools import setup, find_packages
setup(
    name="flask-zmq",
    author="Andrew Grigorev",
    author_email="andrew@ei-grad.ru",
    description="Deferred execution routines for Flask applications using ZeroMQ",
    url="http://github.com/ei-grad/flask-zmq",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask>=0.11',
        'click',
        'pyzmq',
    ],
    entry_points={
        'flask.commands': [
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock'],
)
