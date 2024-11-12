import pytest
from lit_python_sdk import connect
import time

def test_connect_and_execute():
    # Create a client instance
    client = connect()
    
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
