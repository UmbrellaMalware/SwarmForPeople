#!/usr/bin/python

import click

from docker_client import DockerClient
from utils import get_master_from_service_name


@click.group()
def service():
    pass


@click.command()
@click.option("--name", "-n", help="service name", required=True)
@click.option("--master", "-m", help="master swarm node", required=False)
def exec(name, master):
    if not master:
        master = get_master_from_service_name(name)
    docker = DockerClient(master)
    docker.interactive_shell_in_container(docker.get_service_info(name))


@click.command()
def welcome():
    click.echo("Welcome")


service.add_command(exec)
service.add_command(welcome)

if __name__ == "__main__":
    service()
