Configuration files
===================

Each model is one YAML file. The files in ``conf/`` are working examples for every backend.

.. code-block:: yaml

   LLM_VERSION : "gpt-5.2"
   API_KEY_NAME : "OPENAI_API_KEY"

   LLM_CONFIG:
     max_completion_tokens: 16384
     seed: 42

Common keys
-----------

``PROVIDER``
   Backend slug or alias (``azure``, ``claude``, ``hf``, ...). Optional, see
   `Provider selection`_. The aliases are listed in :data:`llm_factory.PROVIDER_ALIASES`.

``LLM_VERSION`` / ``MODEL`` / ``MODEL_NAME``
   Model or deployment name. The first one set wins.

``SYSTEM_MSG``
   System prompt sent ahead of every query.

``DISABLE_SYSTEM``
   Turn system messages into a user/assistant pair, for models whose chat template has no
   system role.

``LLM_CONFIG``
   Request parameters, forwarded to the provider **as-is**.

Request parameters
------------------

``LLM_CONFIG`` is not validated. Write the parameter names the model expects, for example
``max_completion_tokens`` for the gpt-5 family and ``max_tokens`` for older models. A backend
can rename some generic names through :attr:`~llm_base.BaseLLM.PARAM_ALIASES`: Anthropic and
Gemini both accept ``max_tokens`` and ``stop`` and send them under their own names. Local
backends (Hugging Face, vLLM) consume the parameters in-process.

Values read from the environment
--------------------------------

Credentials stay in ``.env`` (see :doc:`usage`). A configuration names the variable instead of
holding the value. :func:`llm_base.resolve_config_value` accepts three forms:

.. code-block:: yaml

   ENDPOINT_ENV : "AZURE_OPENAI_ENDPOINT"   # <KEY>_ENV names the variable
   ENDPOINT : "${AZURE_OPENAI_ENDPOINT}"    # ${VAR} syntax
   ENDPOINT : "AZURE_OPENAI_ENDPOINT"       # bare upper-case name (ENDPOINT and BASE_URL only)

A referenced variable that is unset raises :class:`ValueError`. API keys are read from the
variable named by ``API_KEY_NAME``. The string ``"None"`` counts as unset everywhere.

Provider selection
------------------

When ``PROVIDER`` is missing, :func:`llm_factory.infer_provider` guesses from the other keys, in
this order:

#. ``ENDPOINT``, ``ENDPOINT_ENV`` or ``API_VERSION`` present: ``azure_openai``.
#. Model starting with ``claude``, or key name containing ``anthropic``: ``anthropic``.
#. Model starting with ``gemini``: ``gemini``. Model starting with ``glm``: ``glm``.
#. vLLM engine keys (``TENSOR_PARALLEL_SIZE``, ``GPU_MEMORY_UTILIZATION``, ...) and no API key:
   ``vllm``.
#. ``MODEL_NAME``, ``DEVICE``, ``QUANTIZE`` or ``CACHE_DIR`` and no API key: ``huggingface``.
#. Model starting with ``gpt``, ``o1``, ``o3`` or ``o4``: ``openai``.

Set ``PROVIDER`` when the guess is wrong. Azure ``-pro`` deployments, for example, need
``PROVIDER: "azure_responses"``.

Backend-specific keys
---------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Backend
     - Keys
   * - OpenAI
     - ``API_KEY_NAME`` (default ``OPENAI_API_KEY``), ``BASE_URL``, ``ORGANIZATION``,
       ``PROJECT``, ``IMAGE_DETAIL``
   * - Azure OpenAI
     - ``API_KEY_NAME`` (default ``AZURE_OPENAI_API_KEY``), ``ENDPOINT``, ``API_VERSION``,
       ``DEPLOYMENT``, ``IMAGE_DETAIL``
   * - Azure Responses
     - As Azure OpenAI. ``API_VERSION`` must be ``2025-04-01-preview`` or later.
   * - Anthropic
     - ``API_KEY_NAME`` (default ``ANTHROPIC_API_KEY``), ``BASE_URL``
   * - Gemini
     - ``API_KEY_NAME`` (default ``GEMINI_API_KEY``), ``BASE_URL``
   * - GLM
     - ``API_KEY_NAME`` (default ``GLM_API_KEY``, falls back to ``ZHIPUAI_API_KEY``),
       ``BASE_URL``
   * - Hugging Face
     - ``MODEL_NAME``, ``DEVICE``, ``QUANTIZE`` (0, 4 or 8), ``DEVICE_MAP``, ``MULTI_GPU``,
       ``CACHE_DIR``, ``ENABLE_THINKING``, ``SUPPORTS_IMAGES``
   * - vLLM
     - ``MODEL_NAME``, ``DTYPE``, ``TENSOR_PARALLEL_SIZE``, ``MAX_MODEL_LEN``,
       ``MAX_NUM_SEQS``, ``MAX_NUM_BATCHED_TOKENS``, ``GPU_MEMORY_UTILIZATION``,
       ``SWAP_SPACE``, ``TRUST_REMOTE_CODE``, ``ENABLE_PREFIX_CACHING``,
       ``DISABLE_LOG_STATS``, ``ENFORCE_EAGER``, ``DOWNLOAD_DIR``, ``DOWNLOAD_WORKERS``

Each backend class in :doc:`backends` documents its keys in detail.
