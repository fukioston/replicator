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
- [ ] **Environment setup** — auto-install dependencies, handle version conflicts
- [ ] **Experiment runner** — submit training jobs locally or via SSH (`nohup` / `sbatch` / `torchrun`)
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
pip install -r requirements.txt

# First run will launch an interactive setup wizard
python replicator.py --repo https://github.com/karpathy/micrograd
```

The setup wizard will ask you:
- Where to run experiments (local or SSH remote)
- Where to store cloned repos and outputs
- Which LLM provider and API key to use
- Output language for analysis reports (中文 / English / 日本語)

To re-run the setup wizard:
```sh
python replicator.py --repo <url> --setup
```

## Architecture

```
replicator/
├── replicator.py        # CLI entry point + setup wizard trigger
├── graph.py             # LangGraph graph definition and routing
├── state.py             # ReplicatorState TypedDict
├── setup_config.py      # interactive setup wizard
├── nodes/
│   ├── clone_and_read.py   # git clone + read README/requirements/file tree
│   ├── analyze_code.py     # LLM: generate introduction, file breakdown, plan
│   ├── setup_environment.py   # (coming soon)
│   ├── submit_job.py          # (coming soon)
│   ├── heartbeat_monitor.py   # (coming soon)
│   ├── analyze_results.py     # (coming soon)
│   └── design_experiment.py   # (coming soon)
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
