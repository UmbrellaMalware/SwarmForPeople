import os
import tempfile

import paramiko

from interactive import interactive_shell


class SSHClient:
    def __init__(self, host):
        self.host = host
        self.client = paramiko.SSHClient()
        self.config = paramiko.SSHConfig()
        with open(os.path.expanduser("~/.ssh/config")) as _file:
            self.config.parse(_file)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.connect()
        self.tmp_pem_file = self.create_temp_pem_file()

    def create_temp_pem_file(self):
        stdin, stdout, stderr = self.client.exec_command("cat .ssh/stage-master.pem")
        stdout = stdout.read()
        tmp_file = tempfile.NamedTemporaryFile()
        tmp_file.write(stdout)
        tmp_file.seek(0)
        return tmp_file

    def exec_over_jump(self, host, username, command):
        jhost = self.connect_over_jump(host, username)
        stdin, stdout, stderr = jhost.exec_command(command, get_pty=True)
        stdout = stdout.read()
        jhost.close()
        return stdout

    def connect(self):
        host_config = self.config.lookup(self.host)
        self.client.connect(
            host_config["hostname"],
            key_filename=host_config["identityfile"][0],
            username=host_config["user"],
        )

    def connect_over_jump(self, dest, username):
        vmtransport = self.client.get_transport()
        dest_addr = (dest, 22)
        local_addr = (self.host, 22)
        vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
        jhost = paramiko.SSHClient()
        jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jhost.connect(
            dest, username=username, key_filename=self.tmp_pem_file.name, sock=vmchannel
        )
        return jhost

    @staticmethod
    def start_interactive_shell(conn, start_command=None):
        t = conn.get_transport()
        chan = t.open_session()
        chan.get_pty()
        size = os.get_terminal_size()
        channel = conn.invoke_shell(width=size.columns, height=size.lines)
        interactive_shell(channel, start_command=start_command)
