import os
import subprocess
from .base import RemoteBase


class LocalRunner(RemoteBase):

    def run(self, command: str, timeout: int = 300) -> tuple[int, str, str]:
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr

    def run_background(self, command: str, log_file: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        with open(log_file, "w") as log:
            proc = subprocess.Popen(
                command, shell=True,
                stdout=log, stderr=log,
                start_new_session=True,
            )
        return str(proc.pid)

    def is_alive(self, job_id: str) -> bool:
        code, _, _ = self.run(f"kill -0 {job_id} 2>/dev/null")
        return code == 0

    def tail(self, path: str, lines: int = 50) -> str:
        code, stdout, _ = self.run(f"tail -n {lines} {path}")
        return stdout if code == 0 else ""

    def close(self):
        pass
