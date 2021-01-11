from setuptools import setup

setup(
name='Reddit_ChatBot_Python',
version='1.1.8',
project_urls={"Source": "https://github.com/scrubjay55/Reddit_ChatBot_Python.git"},
url="https://github.com/scrubjay55/Reddit_ChatBot_Python.git",
author='scrubjay55',
license="APLv2",
packages=['Reddit_ChatBot_Python', 'Reddit_ChatBot_Python.Utils', 'Reddit_ChatBot_Python.Utils.FrameModel'],
description='a pretty basic websocket wrapper for reddit chatrooms',
long_description=open('README.rst').read(),
install_requires=[
   "requests",
   "websocket_client",
],
)