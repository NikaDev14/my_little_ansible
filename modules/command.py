import logging
from paramiko.client import SSHClient
from modules.base_module import BaseModule


class CommandModule(BaseModule):
    name: str = "command"
    params = dict(
        command=dict(required=True, type='string'),
        shell=dict(required=True, type='string')
    )

    def __init__(self, params: dict):
        super().__init__(params)
        self.params = params

    def process(self, ssh_client: SSHClient):
        command = self.params['command']
        shell = self.params['shell']

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name}")

        stdin, stdout, stderr = ssh_client.exec_command(
            command=f'echo "#!{shell} \n {command}" > /tmp/command.sh')
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        stdin, stdout, stderr = ssh_client.exec_command(
            command=f'chmod +x /tmp/command.sh')
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        stdin, stdout, stderr = ssh_client.exec_command(
            command=f"/tmp/command.sh")
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=OK")
