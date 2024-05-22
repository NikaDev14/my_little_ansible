import os.path

import paramiko
from paramiko.client import SSHClient
from modules.base_module import BaseModule
import logging


class CopyModule(BaseModule):
    name: str = "copy"
    params = dict(
        src=dict(required=True, type='path'),
        dest=dict(required=True, type='path'),
        backup=dict(required=False, type='bool')
    )

    def __init__(self, params: dict):
        super().__init__(params)
        self.params = params

    def process(self, ssh_client: SSHClient):
        src = self.params['src']
        dest = self.params['dest']
        backup = self.params['backup']
        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} src={src} dest={dest} backup={backup}")

        stdin, stdout, stderr = ssh_client.exec_command(command=f"mkdir -p /tmp/sftp")
        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        if dest[0] == "/":
            stdin, stdout, stderr = ssh_client.exec_command(command=f"sudo mkdir -p {dest}")
        else:
            stdin, stdout, stderr = ssh_client.exec_command(command=f"mkdir -p {dest}")

        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        sftp = ssh_client.open_sftp()
        try:
            put_dir(ssh_client, sftp, src, f"/tmp/sftp")
        except Exception as e:
            logging.error(e)
        sftp.close()

        if dest[0] == "/":
            stdin, stdout, stderr = ssh_client.exec_command(
                command=f"sudo cp {'--backup' if backup else ''} /tmp/sftp/* {dest}")
        else:
            stdin, stdout, stderr = ssh_client.exec_command(
                command=f"cp {'--backup' if backup else ''} /tmp/sftp/* {dest}")

        if stdout.channel.recv_exit_status() != 0:
            logging.info(
                f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=KO")
            logging.error(stderr.read().decode('utf-8'))
            return

        logging.info(
            f"host={ssh_client.get_transport().getpeername()[0]} op={self.name} status=OK")


def put_dir(ssh_client: paramiko.SSHClient, sftp: paramiko.SFTPClient, source, target):
    if os.path.isfile(source):
        logging.info(f"File transfer : {source} {target + '/' + os.path.basename(source)}")
        sftp.put(source, target + "/" + os.path.basename(source))
    else:
        for item in os.listdir(source):
            target_path = target + "/" + item
            source_path = os.path.join(source, item)
            if not os.path.isfile(source_path):
                try:
                    ssh_client.exec_command(f"mkdir {target_path}")
                except OSError:
                    pass
                put_dir(ssh_client, sftp, source_path, target_path)
            else:
                logging.info(f"File transfer : {source_path} {target_path}")
                sftp.put(source_path, target_path)
