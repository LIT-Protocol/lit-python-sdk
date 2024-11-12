# lit-python-sdk

A Python SDK for interacting with the Lit Protocol.

## How it works

The SDK uses a Node.js server that runs the LitNodeClient, to connect to the Lit Network and utilize it. The server is started automatically when the client is instantiated. We use the python package [nodejs-bin](https://pypi.org/project/nodejs-bin/) to automatically download and install Node.js.
