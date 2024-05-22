#!/usr/bin/env python

import argparse
from datetime import datetime
import logging

import paramiko
import yaml
from paramiko.client import SSHClient

from modules.apt import AptModule
from modules.copy import CopyModule
from modules.command import CommandModule
from modules.service import ServiceModule
from modules.sysctl import SysctlModule
from modules.template import TplModule

HOST_USER_NAME = "vagrant"
HOST_PASSWORD = "vagrant"

#main function which execute scripts inot targetted VM 
def main():
    logging.getLogger("paramiko").setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(
        format=str(datetime.now()) + ' - root - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(
        description='Configure remote hosts', prog='My Little Ansible', usage='%(prog)s [options]')
    parser.add_argument('-f', dest='todos_file', type=str, required=True,
                        help='YAML file defining todos')
    parser.add_argument('-i', dest='inventory_file', type=str, required=True,
                        help='YAML file defining hosts')
    args = parser.parse_args()
    hosts = build_inventory_list(args.inventory_file)
    jobs = build_job_list(args.todos_file)
    logging.info(f"processing {len(jobs)} jobs on hosts: {print_ip_hosts(hosts)}")
    
    i = 0
    for job in jobs:
        for name, host_conf in hosts.items():
            client = based_connect(
                host_conf['ssh_address'], host_conf['ssh_port'])
            if job['module'] == 'copy':
                backup = ""
                if "backup" in job['params'].keys():
                    backup = job['params']['backup']

                copy_module = CopyModule(params={
                    'src': job['params']['src'],
                    'dest': job['params']['dest'],
                    'backup': backup
                })
                copy_module.process(ssh_client=client)

            if job['module'] == "apt":
                apt_module = AptModule(params={
                    'name': job['params']['name'],
                    'state': job['params']['state']
                })
                apt_module.process(ssh_client=client)

            if job['module'] == "template":
                template_module = TplModule(params={
                    'src': job['params']['src'],
                    'dest': job['params']['dest'],
                    'vars': job['params']['vars']
                })
                template_module.process(ssh_client=client)

            if job['module'] == "service":
                service_module = ServiceModule(params={
                    'name': job['params']['name'],
                    'state': job['params']['state']
                })
                service_module.process(ssh_client=client)

            if job['module'] == "command":
                shell = "/bin/bash"
                if "shell" in job['params'].keys():
                    shell = job['params']['shell']
                command_module = CommandModule(params={
                    'command': job['params']['command'],
                    'shell': shell
                })
                command_module.process(ssh_client=client)

            if job['module'] == "sysctl":
                sysctl_module = SysctlModule(params={
                    'attribute': job['params']['attribute'],
                    'value': job['params']['value'],
                    'permanent': job['params']['permanent']
                })
                sysctl_module.process(ssh_client=client)

def based_connect(host, port):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=HOST_USER_NAME, password=HOST_PASSWORD)
    return client


def build_inventory_list(inventory_file):
    with open(inventory_file, 'r') as f:
        data_loaded = yaml.safe_load(f)

    return data_loaded['hosts']


def build_job_list(todos_file):
    with open(todos_file, 'r') as f:
        data_loaded = yaml.safe_load(f)

    return data_loaded


def print_ip_hosts(hosts):
    hosts_ip = ""
    count = len(hosts.items())
    for name, host_conf in hosts.items():
        count = count - 1
        hosts_ip += host_conf['ssh_address']
        if count != 0:
            hosts_ip += ","
    return hosts_ip


if __name__ == "__main__":
    main()
