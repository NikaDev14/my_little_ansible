import logging
# needs in order to manipulate dir/files
import os.path
# needs in order to establish sshclient connection
from paramiko.client import SSHClient
from jinja2 import Environment, FileSystemLoader
# includes required files
from modules.base_module import BaseModule

# 
class TplModule(BaseModule):
    name: str = "template"
    params = dict(
        src=dict(required=True, type='path'),
        dest=dict(required=True, type='path'),
        vars=dict(
            listen_port=dict(required=True, type='integer'),
            server_name=dict(required=True, type='string'),
        ),
    )

    def __init__(self, params: dict):
        super().__init__(params)
        self.params = params

    def process(self, ssh_client: SSHClient):
        src = self.params['src']
        dest = self.params['dest']
        vars = self.params['vars']

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} src={src} dest={dest}")

        env = Environment(loader=FileSystemLoader("."), trim_blocks=True)
        result = env.get_template(src).render(**vars)
        tmp_file = open(f"/tmp/{os.path.basename(src)}", "w")
        tmp_file.write(result + "\n")
        tmp_file.close()

        if dest[0] == "/":
            stdin, stdout, stderr = ssh_client.exec_command(command=f"sudo mkdir -p {os.path.dirname(dest)}")
        else:
            stdin, stdout, stderr = ssh_client.exec_command(command=f"mkdir -p {os.path.dirname(dest)}")

        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        sftp = ssh_client.open_sftp()
        sftp.put(f"/tmp/{os.path.basename(src)}", f"/tmp/{os.path.basename(src)}")
        sftp.close()

        if dest[0] == "/":
            stdin, stdout, stderr = ssh_client.exec_command(command=f"sudo mv /tmp/{os.path.basename(src)} {dest}")
            if stdout.channel.recv_exit_status() != 0:
                logging.info(
                    f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
                logging.error(stderr.read().decode('utf-8'))
                return
        else:
            stdin, stdout, stderr = ssh_client.exec_command(command=f"mv /tmp/{os.path.basename(src)} {dest}")
            if stdout.channel.recv_exit_status() != 0:
                logging.info(
                    f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
                logging.error(stderr.read().decode('utf-8'))
                return

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=OK")
