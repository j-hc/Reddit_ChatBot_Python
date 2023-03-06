from setuptools import setup

setup(
    name='Reddit_ChatBot_Python',
    version='1.5.1',
    project_urls={"Source": "https://github.com/scrubjay55/Reddit_ChatBot_Python.git"},
    url="https://github.com/scrubjay55/Reddit_ChatBot_Python.git",
    author='scrubjay55',
    license="APLv2",
    packages=['Reddit_ChatBot_Python', 'Reddit_ChatBot_Python._utils', 'Reddit_ChatBot_Python._api'],
    description='an event-driven chatbot library for reddit chatrooms',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "requests>=2.26.0",
        "websocket_client>=1.2.3",
    ],
)
