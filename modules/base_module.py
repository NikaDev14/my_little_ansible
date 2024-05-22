from paramiko.client import SSHClient


class BaseModule:
    name: str = "anonymous"

    def __init__(self, params: dict):
        self.params = params

    def process(self, ssh_client: SSHClient):
        pass
