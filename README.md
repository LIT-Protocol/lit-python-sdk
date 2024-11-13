# lit-python-sdk

A Python SDK for interacting with the Lit Protocol.

## How it works

The SDK uses a Node.js server that runs the LitNodeClient, to connect to the Lit Network and utilize it. The server is started automatically when the client is instantiated. We use the python package [nodejs-bin](https://pypi.org/project/nodejs-bin/) to automatically download and install Node.js.

## How to use it from python

We need to bundle the dependencies of the nodejs server before this is easy. To do it now, run `npm install` in the `lit_python_sdk/nodejs` folder. Make sure you have the `LIT_PYTHON_SDK_PRIVATE_KEY` environment variable set to your private key.

Then, make sure you have installed:

- pytest `pip install pytest`
- run `pip install -e . ` in the root directory

Finally, run `pytest` to in the root directory to test it.
