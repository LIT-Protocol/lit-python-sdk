import os
import subprocess
import signal
import sys
from pathlib import Path

class NodeServer:
    def __init__(self, port: int):
        self.port = port
        self.process = None
        self.server_folder = Path(__file__).parent / "nodejs"

    def start(self):
        """Starts the Node.js server process"""
        if self.process is not None:
            return

        self.process = subprocess.Popen(
            ["npm", "start"],
            env={**os.environ, "PORT": str(self.port)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.server_folder
        )

    def stop(self):
        """Stops the Node.js server process"""
        if self.process is not None:
            if sys.platform == "win32":
                self.process.send_signal(signal.CTRL_C_EVENT)
            else:
                self.process.terminate()
            self.process.wait()
            self.process = None 