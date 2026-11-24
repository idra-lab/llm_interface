# LLM Interface

A single Python interface to several LLM providers. Each model is described by one YAML file.
You load the file and call `query()`. The backend, connection and request parameters all come
from the file, so switching model means switching file, not code.

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

`llm_base.py` imports its logger from `utility.logger`. It searches for a `utility/logger.py`
in this folder and up to seven parent folders. When you use this repository on its own, add a
`utility/logger.py` that defines a standard `logging.Logger` named `logger`:

```python
# utility/logger.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_interface")
```

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

The full documentation, including the API reference, is built with Sphinx:

```bash
pip install -r docs/requirements.txt
make -C docs html
# open docs/_build/html/index.html
```

## Known limitations

- `BaseLLM.prepare()` (few-shot examples from a folder) is not implemented yet and raises
  `NotImplementedError`.
- `utility/logger.py` is not part of this repository (see Installation).
