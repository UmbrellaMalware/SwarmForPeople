GET_CONTAINER_LIST = """docker ps --format '{"ID":"{{ .ID }}", "Image": "{{ .Image }}", "Names":"{{ .Names }}"}'"""
