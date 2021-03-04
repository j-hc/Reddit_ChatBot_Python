from setuptools import setup

setup(
    name='Reddit_ChatBot_Python',
    version='1.2.2',
    project_urls={"Source": "https://github.com/scrubjay55/Reddit_ChatBot_Python.git"},
    url="https://github.com/scrubjay55/Reddit_ChatBot_Python.git",
    author='scrubjay55',
    license="APLv2",
    packages=['Reddit_ChatBot_Python', 'Reddit_ChatBot_Python.Utils'],
    description='a pretty basic websocket wrapper for reddit chatrooms',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='<=3.8.7',
    install_requires=[
        "requests",
        "websocket_client"
    ],
    extras_require={"extra": ["numpy", "wsaccel"]}
)
