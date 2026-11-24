"""Sphinx configuration for llm_interface."""

import os
import sys

# The modules live in the repository root, and each backend folder is importable from there.
sys.path.insert(0, os.path.abspath(".."))

project = "llm_interface"
author = "Enrico Saccon"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Provider SDKs and heavy local runtimes are not needed to read the docstrings.
# `utility` holds the logger, which comes from the project embedding this repository.
autodoc_mock_imports = [
    "utility",
    "openai",
    "anthropic",
    "google",
    "tiktoken",
    "torch",
    "transformers",
    "huggingface_hub",
    "vllm",
    "PIL",
    "yaml",
    "dotenv",
]

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"

napoleon_numpy_docstring = True
napoleon_google_docstring = False

exclude_patterns = ["_build"]
html_theme = "alabaster"
