import paramiko
from .base import RemoteBase


class SSHRunner(RemoteBase):

    def __init__(self, host: str, user: str, key_path: str):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            host,
            username=user,
            key_filename=key_path,
            timeout=30,
        )

    def run(self, command: str, timeout: int = 300) -> tuple[int, str, str]:
        _, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()

    def run_background(self, command: str, log_file: str) -> str:
        cmd = f"nohup {command} > {log_file} 2>&1 & echo $!"
        _, stdout, _ = self._client.exec_command(cmd)
        return stdout.read().decode().strip()

    def is_alive(self, job_id: str) -> bool:
        code, _, _ = self.run(f"kill -0 {job_id} 2>/dev/null")
        return code == 0

    def tail(self, path: str, lines: int = 50) -> str:
        _, stdout, _ = self._client.exec_command(f"tail -n {lines} {path}")
        return stdout.read().decode()

    def close(self):
        self._client.close()
