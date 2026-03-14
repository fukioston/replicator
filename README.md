# Replicator

> ⚠️ Work in progress. Not ready for use yet.

> Give it a GitHub link. It figures out the rest.

Replicator is an autonomous agent that takes an ML research paper repository and automatically clones it, understands the codebase, sets up the environment, reproduces the results, and iterates on experiments — all with minimal human intervention.

```
Input: GitHub URL + GPU machine
        ↓
① Clone & read README / requirements / configs
        ↓
② Understand code architecture & training pipeline
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
- Every repo has different dependencies, CUDA versions, data formats
- README instructions are often incomplete or outdated
- Debugging environment issues takes hours before any real work begins
- Iterating on experiments requires constant manual intervention

Replicator handles all of this autonomously.

## Features (Roadmap)

- [ ] **Repo analysis** — parse README, requirements, configs, and code structure
- [ ] **Environment setup** — auto-install dependencies, handle version conflicts
- [ ] **Experiment runner** — submit training jobs via SSH, support `nohup` / `sbatch` / `torchrun`
- [ ] **Job monitor** — heartbeat polling, detect completion or crash
- [ ] **Result analysis** — parse logs, metrics, loss curves
- [ ] **Experiment designer** — LLM-driven hyperparameter suggestions based on results
- [ ] **Iteration loop** — automatically run the next experiment when current one finishes

## Supported Models

Replicator works with any Anthropic-compatible LLM:

| Provider | Model |
|----------|-------|
| Anthropic | claude-sonnet-4-6 |
| DeepSeek | deepseek-chat |
| GLM (Zhipu) | glm-5 |
| Kimi (Moonshot) | kimi-k2.5 |
| MiniMax | MiniMax-M2.5 |

## Quick Start

```sh
git clone https://github.com/fukioston/replicator
cd replicator
pip install -r requirements.txt
cp .env.example .env  # fill in your API key and SSH config

python replicator.py --repo https://github.com/author/paper-repo
```

## Configuration

```env
# LLM
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic  # optional
MODEL_ID=deepseek-chat

# GPU machine
SSH_HOST=your.gpu.server
SSH_USER=username
SSH_KEY_PATH=~/.ssh/id_rsa
```

## Architecture

```
replicator/
├── agent/
│   ├── loop.py          # core agent loop
│   ├── tools.py         # tool definitions & handlers
│   └── prompts.py       # system prompts per phase
├── phases/
│   ├── analyze.py       # repo analysis phase
│   ├── setup.py         # environment setup phase
│   ├── run.py           # experiment execution phase
│   └── iterate.py       # result analysis & next experiment
├── remote/
│   └── ssh.py           # SSH connection & job management
└── replicator.py        # entry point
```

## License

MIT
