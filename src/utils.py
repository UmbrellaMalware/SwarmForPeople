def get_container_ids_from_containers_list(containers_list, container_name):
    containers_info = []
    for container in containers_list:
        if container["Names"].split(".")[0] == container_name:
            containers_info.append(container["ID"])
    return containers_info


def get_env_from_host(host):
    mapper = {
        "alao.dev": "dev",
        "alao.release": "release",
        "prod": "master",
    }
    return mapper[host]


def get_pem_file_name_by_env(env):
    mapper = {
        "dev": ".ssh/stage-master.pem",
        "release": "release-master-0.pem",
        "master": "production-master.pem",
    }
    if env in mapper:
        return mapper[env]
    else:
        raise Exception(f"Unknown environment {env}, choose one of {mapper.keys()}")


def get_master_from_service_name(service_name):
    mapper = {
        "dev": "ssh://alao.dev",
        "release": "ssh://alao.release",
        "master": "ssh://prod",
    }
    env = service_name.split("_")[0]
    if env in mapper:
        return mapper[env]
    else:
        raise Exception(
            f"Unknown environment for service {service_name}, choose one of {mapper.keys()} --master key"
        )
