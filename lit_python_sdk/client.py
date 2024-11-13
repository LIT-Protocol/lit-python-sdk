import requests
import subprocess
import time
from .server import NodeServer

class LitClient:
    def __init__(self, port=3092):
        self.port = port
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
    
    def sign(self, to_sign: str, pkp_public_key: str) -> dict:
        """Signs a message with a PKP"""
        response = requests.post(f"http://localhost:{self.port}/sign", json={"toSign": to_sign, "pkpPublicKey": pkp_public_key})
        return response.json()

    def __del__(self):
        """Cleanup: Stop the Node.js server when the client is destroyed"""
        if hasattr(self, 'server'):
            self.server.stop() 