from abc import ABC, abstractmethod


class RemoteBase(ABC):

    @abstractmethod
    def run(self, command: str, timeout: int = 300) -> tuple[int, str, str]:
        """Run a command. Returns (exit_code, stdout, stderr)."""
        ...

    @abstractmethod
    def run_background(self, command: str, log_file: str) -> str:
        """Launch a detached process. Returns job_id (PID or slurm job id)."""
        ...

    @abstractmethod
    def is_alive(self, job_id: str) -> bool:
        """Check if a background job is still running."""
        ...

    @abstractmethod
    def tail(self, path: str, lines: int = 50) -> str:
        """Read the last N lines of a remote/local file."""
        ...

    @abstractmethod
    def close(self):
        ...
