from setuptools import setup

setup(
name='Reddit_ChatBot_Python',
version='1',
author='scrubjay55',
packages=['Reddit_ChatBot_Python', 'Reddit_ChatBot_Python.Utils', 'Reddit_ChatBot_Python.Utils.FrameModel'],
description='a pretty basic websocket wrapper for reddit chatrooms by u/peroksizom',
long_description=open('README.rst').read(),
install_requires=[
   "requests",
   "websocket_client",
],
)