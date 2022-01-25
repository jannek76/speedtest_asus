"""Client to handle connections and actions executed against a remote host."""
from pathlib import Path
import sys
import logging

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException

print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)

class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    def __init__(self, host, port, user, ssh_key_filename):
        self.host = host
        self.port = port
        self.user = user
        self.ssh_key_filename = ssh_key_filename
        self.client = None
        self.scp = None
        self.conn = None

    def __get_ssh_key(self):
        """ Fetch locally stored SSH key."""
        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logging.info(f'Found SSH key at self {self.ssh_key_filepath}')
        except SSHException as error:
            logging.error(error)
        return self.ssh_key

    def __connect(self):
        """Open connection to remote host. """
        if self.conn is None:
            try:
                self.client = SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(AutoAddPolicy())
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.user,
                    key_filename=self.ssh_key_filename,
                    look_for_keys=False,
                    timeout=5000
                )
            except AuthenticationException as error:
                logging.error(f'Authentication failed: did you remember to create an SSH key? {error}')
                raise error
        return self.client

    def disconnect(self):
        """Close SSH & SCP connection."""
        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()

    def execute_commands(self, commands):
        """
        Execute multiple commands in succession.

        :param commands: List of unix commands as strings.
        :type commands: List[str]
        """
        self.conn = self.__connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                logging.debug(f'INPUT: {cmd} | OUTPUT: {line}')
        return response

    def execute_command(self, command):
        """
        Execute multiple command in succession.

        :param command: Unix command as string.
        :type command: str
        """
        self.conn = self.__connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        stdout.channel.recv_exit_status()
        response = stdout.readlines()
        if logging.getLogger().level == logging.DEBUG:
            for line in response:
                logging.debug(f'INPUT: {command} | OUTPUT: {line}')

        return response
