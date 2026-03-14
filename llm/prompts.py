IDENTIFY_FILES_SYSTEM = """You are an ML research engineer. Given a repository's README and file tree, identify the most important files to read for understanding and reproducing the project.

Always respond in valid JSON."""

IDENTIFY_FILES_USER = """Repository: {repo_url}

README:
{readme}

File tree:
{file_tree}

Which files are most important for understanding and reproducing this project?
Respond with JSON:
{{
  "key_files": ["train.py", "model.py", "config.yaml"],
  "reason": "brief explanation of why these files matter"
}}

Rules:
- Include all files that are genuinely important for understanding and reproducing the project — no arbitrary limit
- Only include files that actually appear in the file tree
- Prioritize: training entry point, model definition, config files, data loading
- Skip: tests, docs, README (already provided), utility/helper files that are not critical
"""


PLAN_QUICK_RUN_SYSTEM = """You are an ML research engineer. Your goal is to find the minimum command to verify a project runs without errors — not to complete training, just to confirm the code executes successfully.

Always respond in valid JSON."""

PLAN_QUICK_RUN_USER = """Repository: {repo_url}
Train entrypoint: {train_entrypoint}

Reproduction plan:
{reproduction_plan}

Key source files:
{file_contents}

Plan the minimal command to verify this project runs. Use the smallest possible data, fewest steps/epochs, smallest batch size.

Look for flags like: --max_steps, --max_iters, --num_epochs, --epochs, --steps, --num_train_samples, --limit, --subset, --debug, --dry_run, --fast_dev_run, --overfit_batches

Respond with JSON:
{{
  "cmd": "python train.py --max_steps 2 --batch_size 4",
  "cwd": ".",
  "env_vars": {{}},
  "rationale": "why this is the minimal command that proves the code runs"
}}

Rules:
- cwd is relative to the repo root
- env_vars only if strictly required (e.g. CUDA_VISIBLE_DEVICES=\\"\\")
- If no obvious flags exist, run with defaults and set a timeout
- Prefer CPU-friendly settings if possible
"""


DIAGNOSE_ERROR_SYSTEM = """You are an ML research engineer debugging a failed experiment setup. Analyze the error and give concrete, actionable fixes.

Write your diagnosis in {output_language}."""

DIAGNOSE_ERROR_USER = """Command that failed:
{cmd}

Output / error log:
{log}

Diagnose the error and provide:
1. Root cause (one sentence)
2. Fix steps (numbered, with exact commands where possible)
3. Whether this is likely a missing package, data issue, config issue, or environment issue
"""


ANALYZE_REPO_SYSTEM = """You are an ML research engineer specializing in reproducing academic papers.
Given information about a GitHub repository, you will:
1. Understand what the paper/project is about
2. Identify the key components of the codebase
3. Create a concrete step-by-step reproduction plan

Always respond in valid JSON. Write all text fields in {output_language}."""

ANALYZE_REPO_USER = """Repository: {repo_url}

README:
{readme}

File tree:
{file_tree}

Requirements:
{requirements}

Key source files:
{file_contents}

Analyze this repository and respond with JSON in exactly this format:
{{
  "introduction": "A detailed description of what this project does, its significance, the core idea behind it, and what problem it solves.",
  "file_breakdown": [
    {{
      "path": "engine.py",
      "role": "core autograd engine",
      "description": "Implements the Value class with forward and backward pass. Contains the computational graph building logic and backpropagation through operations like add, mul, tanh, relu."
    }},
    ...list every meaningful file in the repo...
  ],
  "preview": {{
    "framework": "e.g. PyTorch / JAX / TensorFlow / pure Python",
    "architecture": "description of how the components fit together"
  }},
  "reproduction_plan": [
    {{"step": 1, "action": "Install dependencies", "command": "pip install -r requirements.txt"}},
    {{"step": 2, "action": "Download dataset", "command": "python download_data.py"}},
    ...
  ],
  "train_entrypoint": "relative path to the main training script",
  "notes": "any potential issues or things to watch out for"
}}"""
