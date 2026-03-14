# Replicator

[English](./README.md) | [中文](./README-zh.md)

> ⚠️ Work in progress. Not ready for use yet.

> Give it a GitHub link. It figures out the rest.

Replicator is an autonomous agent that takes an ML research paper repository and automatically clones it, analyzes the codebase, sets up the environment, reproduces the results, and iterates on experiments — all with minimal human intervention.

```
Input: GitHub URL
        ↓
① Clone & read README / requirements / configs
        ↓
② Analyze code architecture → generate introduction, file breakdown & reproduction plan
        ↓
③ Set up environment & dependencies
        ↓
④ Run baseline experiment (original paper config)
        ↓
⑤ Monitor → Analyze results → Design next experiment
        ↓
        loop
```

## Motivation

Reproducing ML papers is tedious:
- Every repo has different dependencies, CUDA versions, and data formats
- README instructions are often incomplete or outdated
- Debugging environment issues takes hours before any real work begins
- Iterating on experiments requires constant manual intervention

Replicator handles all of this autonomously.

## Features (Roadmap)

- [x] **Repo analysis** — clone repo, parse README, requirements, and file structure
- [x] **Code understanding** — LLM generates introduction, per-file breakdown, and reproduction plan
- [x] **Environment setup** — LLM reads README and runs correct setup commands (conda / venv / pip)
- [x] **Quick run** — LLM plans minimal command (smallest data/steps), asks user for API keys, confirms code runs, kills after first step
- [x] **Error diagnosis** — if run fails, LLM analyzes traceback and suggests fixes
- [ ] **Full experiment runner** — submit training jobs locally or via SSH (`nohup` / `sbatch` / `torchrun`)
- [ ] **Job monitor** — heartbeat polling, detect completion or crash
- [ ] **Result analysis** — parse logs, metrics, loss curves
- [ ] **Experiment designer** — LLM-driven hyperparameter suggestions based on results
- [ ] **Iteration loop** — automatically run the next experiment when current one finishes

## Supported LLM Providers

| Provider | Model |
|----------|-------|
| Anthropic | claude-sonnet-4-6 |
| DeepSeek | deepseek-chat |
| GLM (Zhipu) | glm-4 |
| Kimi (Moonshot) | moonshot-v1-8k |
| MiniMax | MiniMax-M2.5 |
| Any OpenAI-compatible API | custom |

## Quick Start

```sh
git clone https://github.com/fukioston/replicator
cd replicator
pip install -e .

# Run the setup wizard (choose LLM provider, API key, output language)
replicator config

# Create a task
replicator create -n my-exp --repo https://github.com/karpathy/micrograd

# Run analysis + quick run
replicator run -n my-exp

# List all tasks
replicator list

# View task details
replicator show my-exp
```

The setup wizard will ask you:
- Where to store cloned repos and outputs
- Which LLM provider and API key to use
- Output language for analysis reports (中文 / English / 日本語)

## Architecture

```
replicator/
├── cli.py               # CLI entry point (typer subcommands)
├── replicator.py        # task runner, wires graph to CLI
├── graph.py             # LangGraph graph definition and routing
├── state.py             # ReplicatorState TypedDict
├── setup_config.py      # interactive setup wizard
├── tasks.py             # task persistence (tasks.json)
├── nodes/
│   ├── clone_and_read.py      # git clone + read README/requirements/file tree
│   ├── identify_key_files.py  # LLM: pick important files to read
│   ├── analyze_code.py        # LLM: introduction, file breakdown, reproduction plan
│   ├── setup_env.py           # LLM-guided env setup (conda/venv/pip)
│   ├── plan_quick_run.py      # LLM: minimal command to verify the code runs
│   ├── gather_user_inputs.py  # interactive: ask user for API keys, dataset paths, etc.
│   ├── execute_quick_run.py   # run the command, kill after first step confirmed
│   └── diagnose_error.py      # LLM: analyze traceback and suggest fixes
├── remote/
│   ├── base.py          # abstract runner interface
│   ├── local.py         # local subprocess runner
│   └── ssh.py           # SSH runner (paramiko)
└── llm/
    ├── client.py         # build LLM client (Anthropic or OpenAI-compatible)
    └── prompts.py        # system and user prompts
```

## License

MIT
