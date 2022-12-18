import json
from typing import Any
from typing import List

import docker
from docker.models.nodes import Node
from docker.models.services import Service

from commands_helper import GET_CONTAINER_LIST
from ssh_client import SSHClient
from utils import get_container_ids_from_containers_list


class DockerClient:
    def __init__(self, master_node):
        self.client = docker.DockerClient(base_url=master_node, use_ssh_client=True)
        self.master_node = master_node.replace("ssh://", "")
        self.ssh_client = SSHClient(self.master_node)

    def get_service_info(self, service_name: str) -> Service:
        return self.client.services.get(service_name)

    def get_nodes(self):
        return self.client.nodes.list()

    def get_nodes_by_service(self, service: Service) -> [Node]:
        tasks = service.tasks(filters={"desired-state": "Running"})
        return [self.client.nodes.get(i["NodeID"]) for i in tasks]

    def get_service_nodes_ip(self, service: Service) -> list[str]:
        return [self.get_node_ip(i) for i in self.get_nodes_by_service(service)]

    def get_containers_on_node(self, node: Node) -> List[str]:
        node_ip = self.get_node_ip(node)
        stdout = (
            self.ssh_client.exec_over_jump(node_ip, "ubuntu", GET_CONTAINER_LIST)
            .decode("utf-8")
            .split("\r\n")
        )
        return [json.loads(i) for i in stdout if i]

    def get_container_ids_by_service(
        self, service: Service
    ) -> list[dict[str, str | Any]]:
        nodes = self.get_nodes_by_service(service)
        container_ids = []
        for node in nodes:
            containers = self.get_containers_on_node(node)
            ids = get_container_ids_from_containers_list(containers, service.name)
            # TODO change to namedtuple
            container_ids.extend(
                [{"node_ip": self.get_node_ip(node), "containers": ids}]
            )
        return container_ids

    def interactive_shell_in_container(self, service: Service, start_command="bash"):
        node = self.get_container_ids_by_service(service)[0]
        node_ip = node["node_ip"]
        container = node["containers"][0]
        conn = self.ssh_client.connect_over_jump(node_ip, "ubuntu")
        self.ssh_client.start_interactive_shell(
            conn, f"docker exec -it {container} {start_command}\n"
        )

    @staticmethod
    def get_node_ip(node: Node) -> str:
        hostname = node.attrs["Description"]["Hostname"].replace("ip-", "")
        hostname.replace("-", ".")
        return hostname.replace("-", ".")
