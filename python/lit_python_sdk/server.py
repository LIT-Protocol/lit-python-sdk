import os
import subprocess
import signal
import sys
from pathlib import Path

class NodeServer:
    def __init__(self, port: int):
        self.port = port
        self.process = None
        self.server_folder = Path(__file__).parent / "../../js-sdk-server"

    def start(self):
        """Starts the Node.js server process"""
        if self.process is not None:
            return

        log_file = open(self.server_folder / "server.log", "w")
        self.process = subprocess.Popen(
            ["npm", "start"],
            env={**os.environ, "PORT": str(self.port)},
            stdout=log_file,
            stderr=log_file,
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