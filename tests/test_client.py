import pytest
from lit_python_sdk import connect
import time

client = connect()


def test_connect_and_execute():    
    # Give the server a moment to fully initialize
    time.sleep(2)
    
    # Execute a simple JavaScript code
    js_code = """
        (async () => {
            console.log("This is a log");
            Lit.Actions.setResponse({response: "Hello, World!"});
        })()
    """
    
    result = client.execute_js(js_code)

    print(result)
    
    # Check if the execution was successful
    # correct response is {'success': True, 'signedData': {}, 'decryptedData': {}, 'claimData': {}, 'response': 'Hello, World!', 'logs': 'This is a log\n'}
    assert result['success'] == True, "Expected success to be True"
    assert result['response'] == 'Hello, World!', "Expected response to be 'Hello, World!'"
    assert result['logs'] == 'This is a log\n', "Expected logs to be 'This is a log\n'"

def test_create_wallet_and_sign():
    wallet = client.create_wallet()
    print(wallet)
    to_sign = "0xadb20420bde8cda6771249188817098fca8ccf8eef2120a31e3f64f5812026bf"
    signature = client.sign(to_sign, wallet['pkp']['publicKey'])
    print(signature)
