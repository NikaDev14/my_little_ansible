import logging

from paramiko.client import SSHClient
from modules.base_module import BaseModule


class AptModule(BaseModule):
    name: str = "copy"
    params = dict(
        name=dict(required=True, type='string'),
        state=dict(required=True, type='string'),
    )

    def __init__(self, params: dict):
        super().__init__(params)
        self.params = params

    def process(self, ssh_client: SSHClient):
        name = self.params['name']
        state = self.params['state']

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} name={name} state={state}")

        action = "install"
        if state == "present":
            action = "purge"

        stdin, stdout, stderr = ssh_client.exec_command(command=f"sudo apt -y {action} {name}")
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return
        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=OK")

