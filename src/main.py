#!/usr/bin/python

import click

from docker_client import DockerClient


@click.group()
def service():
    pass


@click.command()
@click.option("--name", "-n", help="service name", required=True)
@click.option("--master", "-m", help="master swarm node", required=True)
def exec(name, master):
    docker = DockerClient(master)
    docker.interactive_shell_in_container(docker.get_service_info(name))


@click.command()
def welcome():
    click.echo("Welcome")


service.add_command(exec)
service.add_command(welcome)

if __name__ == "__main__":
    service()
