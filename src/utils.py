def get_container_ids_from_containers_list(containers_list, container_name):
    containers_info = []
    for container in containers_list:
        if container["Names"].split('.')[0] == container_name:
            containers_info.append(container['ID'])
    return containers_info
