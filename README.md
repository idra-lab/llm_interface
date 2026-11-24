# LLM Interface

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pyright](https://img.shields.io/badge/types-pyright-informational)](https://github.com/microsoft/pyright)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Docs](https://github.com/idra-lab/llm_interface/actions/workflows/docs.yml/badge.svg)](https://idra-lab.github.io/llm_interface/)

[![OpenAI](https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white)](https://platform.openai.com/)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/products/ai-services/openai-service)
[![Anthropic](https://img.shields.io/badge/Anthropic-191919?logo=anthropic&logoColor=white)](https://www.anthropic.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![GLM](https://img.shields.io/badge/GLM-1F6FEB)](https://open.bigmodel.cn/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![vLLM](https://img.shields.io/badge/vLLM-30A2FF)](https://github.com/vllm-project/vllm)

A single Python interface to several LLM providers. Each model is described by one YAML file.
You load the file and call `query()`. The backend, connection and request parameters all come
from the file, so switching model means switching file, not code.

## Contents

- [Repository layout](#repository-layout)
- [Installation](#installation)
  - [Linux](#linux)
  - [macOS](#macos)
  - [Windows](#windows)
- [Credentials](#credentials)
- [Quick start](#quick-start)
- [Examples](#examples)
- [Configuration files](#configuration-files)
  - [Provider selection](#provider-selection)
  - [Backend-specific keys](#backend-specific-keys)
- [Adding a backend](#adding-a-backend)
- [Documentation](#documentation)
- [Known limitations](#known-limitations)

Supported backends:

| Provider slug            | Class                     | Runs        | Images Support |
|--------------------------|---------------------------|-------------|--------|
| `openai`                 | `LLMOpenAI`               | API         | yes    |
| `azure_openai`           | `LLMAzureOpenAI`          | API         | yes    |
| `azure_openai_responses` | `LLMAzureOpenAIResponses` | API         | yes    |
| `anthropic`              | `LLMAnthropic`            | API         | yes    |
| `gemini`                 | `LLMGemini`               | API         | yes    |
| `glm`                    | `LLMGLM`                  | API         | yes    |
| `huggingface`            | `LLMHuggingFace`          | in-process  | depends on the model |
| `vllm`                   | `LLMVLLM`                 | in-process  | no     |

## Repository layout

```
llm_base.py        BaseLLM, environment and config helpers, message and image utilities
llm_factory.py     picks the backend for a config file: create_llm(), select_llm()
LLM<Provider>/     one folder per backend, each with its own requirements.txt
conf/              ready-made YAML configurations, one per model
models/            local model weights (ignored by git)
docs/              Sphinx documentation
examples/          runnable text and image examples
utility/           shared logger
.env.example       template for the credentials file
```

## Installation

```bash
pip install -r requirements.txt            # every API backend + Hugging Face
pip install -r LLMVLLM/requirements.txt    # vLLM, Linux only, optional
```

Each backend folder has its own `requirements.txt`, so you can install only the providers you use:

```bash
pip install pyyaml python-dotenv pillow -r LLMOpenAI/requirements.txt
```

Logging goes through `utility/logger.py`. It writes to the console and to a rotating `log.log`
file. It uses [loguru](https://github.com/Delgan/loguru) when installed (`pip install loguru`),
and the standard `logging` module otherwise.

### Linux

Every backend works on Linux, vLLM included. The commands below are for Ubuntu and Debian; on
Fedora, replace the `apt` line with `sudo dnf install -y python3 python3-pip git make`.

1. Install Python 3.10 or later and Git:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git make
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/idra-lab/llm_interface.git
   cd llm_interface
   ```

3. Create a virtual environment, install the requirements and create the credentials file:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r LLMVLLM/requirements.txt    # optional
   cp .env.example .env
   ```

Notes for Linux:

- **GPU:** the PyTorch wheels on PyPI already include CUDA. You only need the NVIDIA driver;
  run `nvidia-smi` to check that the GPU is visible.
- **Model folder:** some Hugging Face and vLLM configurations in `conf/` download weights to
  `/scratch/models`. Create it (`sudo mkdir -p /scratch/models && sudo chown $USER /scratch/models`)
  or change `CACHE_DIR` / `DOWNLOAD_DIR` to a folder of your own.

### macOS

The API backends and the Hugging Face backend work on macOS. vLLM does not:
`LLMVLLM/requirements.txt` installs nothing there.

1. Install [Homebrew](https://brew.sh/), then Python and Git:

   ```bash
   brew install python@3.12 git
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/idra-lab/llm_interface.git
   cd llm_interface
   ```

3. Create a virtual environment, install the requirements and create the credentials file:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

Notes for macOS:

- **Hugging Face models:** the configurations in `conf/` set `DEVICE: "cuda"`, which a Mac does
  not have. Set `DEVICE: "mps"` to use the GPU of an Apple Silicon Mac, or `"cpu"`.
- **Quantization:** `bitsandbytes` has no macOS build and is skipped, so `QUANTIZE` has no
  effect and models load at full size. Large models may not fit in memory.
- **Model folder:** `/scratch/models` cannot be created on macOS without extra steps. Delete the
  `CACHE_DIR` line from the Hugging Face configuration to download into the repository's
  `models/` folder, or set a full path such as `/Users/<you>/models` (`~` is not expanded).

### Windows

On Windows, run the project inside [WSL 2](https://learn.microsoft.com/windows/wsl/install)
(Windows Subsystem for Linux). Every backend works there, vLLM included.

1. Install WSL with Ubuntu. Open PowerShell **as administrator**, run the command below, and
   restart Windows when it asks:

   ```powershell
   wsl --install -d Ubuntu
   ```

2. Open *Ubuntu* from the Start menu and choose a Linux user name and password.

3. In that Ubuntu terminal, follow the [Linux](#linux) steps above. Clone the repository into the
   Linux home folder (`cd ~` first): code under `/mnt/c/...` also works, but file access there is
   much slower.

Notes for WSL:

- **GPU:** install the normal NVIDIA driver on Windows only. WSL passes the GPU through, so do
  not install a Linux NVIDIA driver inside Ubuntu. Run `nvidia-smi` in Ubuntu to check that the
  GPU is visible.
- **Windows files:** your Windows drives are under `/mnt/c`, `/mnt/d`, and so on. From Windows,
  open the Linux files by typing `\\wsl$\Ubuntu` in the Explorer address bar.

## Credentials

Copy `.env.example` to `.env` in the repository root and fill in the keys you need:

```bash
cp .env.example .env
```

The `.env` file is read from the folder that contains `llm_base.py`, wherever you run your
script from. Variables already set in the shell take precedence. To read a different file, or
none at all:

```python
from llm_base import configure_env

configure_env("other.env")  # read other.env instead
configure_env(load=False)  # use the shell environment only
```

The YAML files never hold secrets. They name the environment variable to read, through
`API_KEY_NAME`, `ENDPOINT_ENV` or `BASE_URL_ENV`.

## Quick start

```python
from llm_factory import create_llm

llm = create_llm("conf/gpt52.yaml")
ok, answer = llm.query("Summarise the plot of Hamlet in one sentence.")
if ok:
    print(answer)
    print(llm.last_usage)  # {'prompt_tokens': ..., 'completion_tokens': ...}
```

With images (PIL images or file paths), on a backend that supports them:

```python
ok, answer = llm.query("What is in this picture?", images=["photo.jpg"])
```

Keep the conversation going across calls:

```python
llm.query("My name is Ada.", keep_history=True)
ok, answer = llm.query("What is my name?", keep_history=True)
```

Pick a config interactively from `conf/`, or by index or file name:

```python
from llm_factory import select_llm

llm = select_llm()  # prints a numbered menu
llm = select_llm(selection="glm4_7.yaml")
```

Override values from the file at load time:

```python
llm = create_llm("conf/gpt52.yaml", model="gpt-5.4", params={"seed": 7})
```

`query()` returns `(success, answer)`. It retries up to `max_retry` times (default 3) and
returns `(False, "")` when every attempt fails. It does not raise on provider errors.

## Examples

The `examples/` folder holds two runnable scripts. Both use `conf/azure_gpt52.yaml`, so they need
`AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` in `.env`.

| Script | What it does |
|--------|--------------|
| [`examples/text_query.py`](examples/text_query.py) | Sends a text-only question and prints the answer and token usage. |
| [`examples/image_query.py`](examples/image_query.py) | Downloads Hokusai's *The Great Wave off Kanagawa* (public domain, Wikimedia Commons) and asks the model to describe it. |

```bash
python examples/text_query.py
python examples/image_query.py
```

To try another model, change `CONFIG_FILE` at the top of the script.

## Configuration files

A minimal configuration:

```yaml
LLM_VERSION : "gpt-5.2"
API_KEY_NAME : "OPENAI_API_KEY"

LLM_CONFIG:
  max_completion_tokens: 16384
  seed: 42
```

Keys shared by every backend:

| Key | Meaning |
|-----|---------|
| `PROVIDER` | Backend slug or alias (`azure`, `claude`, `hf`, ...). Optional, see below. |
| `LLM_VERSION` / `MODEL` / `MODEL_NAME` | Model or deployment name. The first one set wins. |
| `SYSTEM_MSG` | System prompt sent ahead of every query. |
| `DISABLE_SYSTEM` | Turn system messages into a user/assistant pair, for models without a system role. |
| `LLM_CONFIG` | Request parameters, forwarded to the provider **as-is**. |

`LLM_CONFIG` is not validated. Write the parameter names the model expects, for example
`max_completion_tokens` for the gpt-5 family and `max_tokens` for older models. Some backends
rename a few generic names: Anthropic and Gemini turn `max_tokens` and `stop` into their own names.

Any value can come from the environment in one of three ways:

```yaml
ENDPOINT_ENV : "AZURE_OPENAI_ENDPOINT"   # <KEY>_ENV names the variable
ENDPOINT : "${AZURE_OPENAI_ENDPOINT}"    # ${VAR} syntax
ENDPOINT : "AZURE_OPENAI_ENDPOINT"       # bare upper-case name (ENDPOINT and BASE_URL only)
```

The string `"None"` counts as unset.

### Provider selection

When `PROVIDER` is missing, `llm_factory.infer_provider()` guesses from the other keys:

1. `ENDPOINT`, `ENDPOINT_ENV` or `API_VERSION` present: `azure_openai`.
2. Model starting with `claude`, or key name containing `anthropic`: `anthropic`.
3. Model starting with `gemini`: `gemini`. Model starting with `glm`: `glm`.
4. vLLM engine keys (`TENSOR_PARALLEL_SIZE`, `GPU_MEMORY_UTILIZATION`, ...) and no API key: `vllm`.
5. `MODEL_NAME`, `DEVICE`, `QUANTIZE` or `CACHE_DIR` and no API key: `huggingface`.
6. Model starting with `gpt`, `o1`, `o3`, `o4`: `openai`.

Set `PROVIDER` explicitly when the guess is wrong. For example, Azure `-pro` deployments need
`PROVIDER: "azure_responses"`.

### Backend-specific keys

| Backend | Keys |
|---------|------|
| OpenAI | `API_KEY_NAME` (default `OPENAI_API_KEY`), `BASE_URL`, `ORGANIZATION`, `PROJECT`, `IMAGE_DETAIL` |
| Azure OpenAI | `API_KEY_NAME` (default `AZURE_OPENAI_API_KEY`), `ENDPOINT`, `API_VERSION`, `DEPLOYMENT`, `IMAGE_DETAIL` |
| Azure Responses | as Azure OpenAI; `API_VERSION` must be `2025-04-01-preview` or later |
| Anthropic | `API_KEY_NAME` (default `ANTHROPIC_API_KEY`), `BASE_URL` |
| Gemini | `API_KEY_NAME` (default `GEMINI_API_KEY`), `BASE_URL` |
| GLM | `API_KEY_NAME` (default `GLM_API_KEY`, falls back to `ZHIPUAI_API_KEY`), `BASE_URL` |
| Hugging Face | `MODEL_NAME`, `DEVICE`, `QUANTIZE` (0/4/8), `DEVICE_MAP`, `MULTI_GPU`, `CACHE_DIR`, `ENABLE_THINKING`, `SUPPORTS_IMAGES` |
| vLLM | `MODEL_NAME`, `DTYPE`, `TENSOR_PARALLEL_SIZE`, `MAX_MODEL_LEN`, `MAX_NUM_SEQS`, `MAX_NUM_BATCHED_TOKENS`, `GPU_MEMORY_UTILIZATION`, `SWAP_SPACE`, `TRUST_REMOTE_CODE`, `ENABLE_PREFIX_CACHING`, `DISABLE_LOG_STATS`, `ENFORCE_EAGER`, `DOWNLOAD_DIR`, `DOWNLOAD_WORKERS` |

See `conf/` for a working example of each.

## Adding a backend

1. Create `LLMMyProvider/LLMMyProvider.py` with a class `LLMMyProvider(BaseLLM)`.
2. Set `PROVIDER`, and `SUPPORTS_IMAGES` if it accepts images.
3. Implement `_create_client()`, `_send(client, messages)` and `_extract_text(response)`.
   Override `_setup()` to read provider keys, `_extract_usage()` for token counts, and
   `image_part()` for images.
4. Register the slug in `PROVIDER_ALIASES` and `PROVIDER_MODULES` in `llm_factory.py`.

## Documentation

The full documentation, including the API reference, is published at
<https://idra-lab.github.io/llm_interface/>. It is rebuilt on every push to `main`.

To build it locally:

```bash
pip install -r docs/requirements.txt
make -C docs html
# open docs/_build/html/index.html
```

## Known limitations

- `BaseLLM.prepare()` (few-shot examples from a folder) is not implemented yet and raises
  `NotImplementedError`.
