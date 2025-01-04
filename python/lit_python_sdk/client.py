import requests
import subprocess
import time
from .server import NodeServer

class LitClient:
    def __init__(self, port=3092):
        self.port = port
        # Check if server is already running by trying to connect
        try:
            response = requests.post(f"http://localhost:{port}/isReady")
            if response.json().get("ready"):
                # Server already running, don't start a new one
                self.server = None
                return
        except requests.exceptions.ConnectionError:
            # Server not running, start it
            self.server = NodeServer(port)
            self._start_server()

    def _start_server(self):
        """Starts the Node.js server and waits for it to be ready"""
        self.server.start()
        self._wait_for_server()

    def _wait_for_server(self, timeout=10):
        """Waits for the server to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.post(f"http://localhost:{self.port}/isReady")
                result = response.json()
                if result.get("ready"):
                    return
                else:
                    time.sleep(0.1)
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
                
        raise TimeoutError("Server failed to start within timeout period")
    
    def set_auth_token(self, auth_token: str) -> dict:
        """Sets the auth token on the Node.js server"""
        response = requests.post(
            f"http://localhost:{self.port}/setAuthToken",
            json={"authToken": auth_token},
        )
        return response.json()

    def execute_js(self, code: str) -> dict:
        """Executes JavaScript code on the Node.js server"""
        response = requests.post(
            f"http://localhost:{self.port}/executeJs",
            json={"code": code}
        )
        return response.json()
    
    def create_wallet(self) -> dict:
        """Creates a new wallet on the Node.js server"""
        response = requests.post(f"http://localhost:{self.port}/createWallet")
        return response.json()
    
    def get_pkp(self) -> dict:
        """Gets the PKP from the Node.js server"""
        response = requests.get(f"http://localhost:{self.port}/pkp")
        return response.json()
    
    def sign(self, to_sign: str) -> dict:
        """Signs a message with a PKP"""
        response = requests.post(f"http://localhost:{self.port}/sign", json={"toSign": to_sign})
        return response.json()

    def __del__(self):
        """Cleanup: Stop the Node.js server when the client is destroyed"""
        if hasattr(self, 'server') and self.server is not None:
            self.server.stop() 