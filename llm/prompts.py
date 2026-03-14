ANALYZE_REPO_SYSTEM = """You are an ML research engineer specializing in reproducing academic papers.
Given information about a GitHub repository, you will:
1. Understand what the paper/project is about
2. Identify the key components of the codebase
3. Create a concrete step-by-step reproduction plan

Always respond in valid JSON."""

ANALYZE_REPO_USER = """Repository: {repo_url}

README:
{readme}

File tree:
{file_tree}

Requirements:
{requirements}

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
