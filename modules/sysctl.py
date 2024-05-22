import logging
from paramiko.client import SSHClient
from modules.base_module import BaseModule


class SysctlModule(BaseModule):
    name: str = "sysctl"
    params = dict(
        attribute=dict(required=True, type='string'),
        value=dict(required=True, type='string'),
        permanent=dict(required=True, type='bool')
    )

    def __init__(self, params: dict):
        super().__init__(params)
        self.params = params

    def process(self, ssh_client: SSHClient):
        attribute = self.params['attribute']
        value = self.params['value']
        permanent = self.params['permanent']

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} "
            f"attribute={attribute} value={value} permanent={permanent}")

        stdin, stdout, stderr = ssh_client.exec_command(command=f"sysctl -w {attribute}={value}")
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        if permanent:
            stdin, stdout, stderr = ssh_client.exec_command(
                command=f'sudo /bin/su -c "echo {attribute} = {value} >> /etc/sysctl.conf"')
            if stdout.channel.recv_exit_status() != 0:
                logging.info(
                    f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
                logging.error(stderr.read().decode('utf-8'))
                return

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=OK")
