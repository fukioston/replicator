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
- Maximum 8 files
- Only include files that actually appear in the file tree
- Prioritize: training entry point, model definition, config files, data loading
- Skip: tests, docs, README (already provided)
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
