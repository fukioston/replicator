"""
Interactive setup wizard. Runs on first launch or when --setup is passed.
Saves config to .replicator.json in the current directory.
"""

import json
import os
from pathlib import Path

CONFIG_FILE = Path(".replicator.json")


def ask(prompt: str, default: str = "") -> str:
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value or default
    value = input(f"{prompt}: ").strip()
    return value


def ask_choice(prompt: str, choices: list[str]) -> str:
    print(f"\n{prompt}")
    for i, c in enumerate(choices, 1):
        print(f"  {i}. {c}")
    while True:
        raw = input("Choice: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        print("Invalid choice, try again.")


def run_setup() -> dict:
    print("\n=== Replicator Setup ===\n")

    config = {}

    # Where to run experiments
    runner_type = ask_choice(
        "Where do you want to run experiments?",
        ["Local machine", "SSH remote server"],
    )
    config["runner"] = "local" if runner_type == "Local machine" else "ssh"

    if config["runner"] == "ssh":
        print()
        config["ssh_host"] = ask("SSH Host")
        config["ssh_user"] = ask("SSH User", default=os.environ.get("USER", ""))
        config["ssh_key_path"] = ask("SSH Key Path", default="~/.ssh/id_rsa")

    # Where to store cloned repos and experiment outputs
    print()
    default_workspace = str(Path.home() / "replicator-workspace")
    config["workspace_dir"] = ask(
        "Where should cloned repos and experiment outputs be stored?",
        default=default_workspace,
    )

    # LLM config
    print()
    llm_choice = ask_choice(
        "Which LLM provider?",
        ["DeepSeek", "Anthropic (Claude)", "GLM (Zhipu)", "Kimi (Moonshot)", "MiniMax", "Other (OpenAI-compatible)"],
    )
    if llm_choice == "DeepSeek":
        config["llm_provider"] = "openai_compatible"
        config["llm_base_url"] = "https://api.deepseek.com/v1"
        config["llm_model"] = "deepseek-chat"
    elif llm_choice == "Anthropic (Claude)":
        config["llm_provider"] = "anthropic"
        config["llm_base_url"] = ""
        config["llm_model"] = ask("Model ID", default="claude-sonnet-4-6")
    elif llm_choice == "GLM (Zhipu)":
        config["llm_provider"] = "openai_compatible"
        config["llm_base_url"] = "https://open.bigmodel.cn/api/paas/v4"
        config["llm_model"] = "glm-4"
    elif llm_choice == "Kimi (Moonshot)":
        config["llm_provider"] = "openai_compatible"
        config["llm_base_url"] = "https://api.moonshot.cn/v1"
        config["llm_model"] = "moonshot-v1-8k"
    elif llm_choice == "MiniMax":
        config["llm_provider"] = "openai_compatible"
        config["llm_base_url"] = "https://api.minimaxi.com/v1"
        config["llm_model"] = "MiniMax-M2.5"
    else:
        config["llm_provider"] = "openai_compatible"
        config["llm_base_url"] = ask("API Base URL")
        config["llm_model"] = ask("Model ID")

    config["llm_api_key"] = ask("API Key")

    # Max iterations
    print()
    raw = ask("Max experiment iterations", default="5")
    config["max_iterations"] = int(raw) if raw.isdigit() else 5

    # Save
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    print(f"\nConfig saved to {CONFIG_FILE.resolve()}\n")
    return config


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return run_setup()
    return json.loads(CONFIG_FILE.read_text())
