from .base import RemoteBase
from .local import LocalRunner
from .ssh import SSHRunner


def build_runner(config: dict) -> RemoteBase:
    if config["runner"] == "ssh":
        return SSHRunner(
            host=config["ssh_host"],
            user=config["ssh_user"],
            key_path=config["ssh_key_path"],
        )
    return LocalRunner()


__all__ = ["RemoteBase", "LocalRunner", "SSHRunner", "build_runner"]
