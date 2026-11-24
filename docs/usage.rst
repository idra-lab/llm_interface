Usage
=====

Installation
------------

.. code-block:: bash

   pip install -r requirements.txt            # every API backend + Hugging Face
   pip install -r LLMVLLM/requirements.txt    # vLLM, Linux only, optional

Each backend folder has its own ``requirements.txt``, so you can install only the providers you
use.

Logging goes through ``utility/logger.py``. It writes to the console and to a rotating
``log.log`` file. It uses `loguru <https://github.com/Delgan/loguru>`_ when installed, and the
standard :mod:`logging` module otherwise.

Credentials
-----------

Copy ``.env.example`` to ``.env`` in the repository root and fill in the keys you need. The file
is read from the folder that contains ``llm_base.py``, wherever you run your script from.
Variables already set in the shell take precedence.

To read a different file, or none at all, call :func:`llm_base.configure_env` before building a
backend:

.. code-block:: python

   from llm_base import configure_env

   configure_env("other.env")     # read other.env instead
   configure_env(load=False)      # use the shell environment only

The YAML files never hold secrets. They name the environment variable to read, see
:doc:`configuration`.

Querying a model
----------------

:func:`llm_factory.create_llm` reads a configuration file, picks the backend and returns a ready
instance. :meth:`~llm_base.BaseLLM.query` returns ``(success, answer)``:

.. code-block:: python

   from llm_factory import create_llm

   llm = create_llm("conf/gpt52.yaml")
   ok, answer = llm.query("Summarise the plot of Hamlet in one sentence.")
   if ok:
       print(answer)
       print(llm.last_usage)   # {'prompt_tokens': ..., 'completion_tokens': ...}

``query()`` retries up to ``max_retry`` times (default 3) and returns ``(False, "")`` when every
attempt fails. It does not raise on provider errors; pass ``end_when_error=True`` to stop at the
first failure.

The connection is opened on the first query and reused afterwards. Local backends load the
weights at that moment, so building the instance stays cheap.

Images
~~~~~~

Backends with :attr:`~llm_base.BaseLLM.SUPPORTS_IMAGES` set accept PIL images or file paths:

.. code-block:: python

   ok, answer = llm.query("What is in this picture?", images=["photo.jpg"])

A text-only backend raises :class:`NotImplementedError`.

Conversation history
~~~~~~~~~~~~~~~~~~~~

With ``keep_history=True`` the exchange is appended to :attr:`~llm_base.BaseLLM.messages` and
sent ahead of the next query:

.. code-block:: python

   llm.query("My name is Ada.", keep_history=True)
   ok, answer = llm.query("What is my name?", keep_history=True)

Choosing a configuration
~~~~~~~~~~~~~~~~~~~~~~~~

:func:`llm_factory.select_llm` lists the files in ``conf/`` and builds the one you pick, by
1-based index, by file name, or interactively:

.. code-block:: python

   from llm_factory import select_llm

   llm = select_llm()                           # prints a numbered menu
   llm = select_llm(selection="glm4_7.yaml")

Overrides
~~~~~~~~~

Keyword arguments override the file. ``params`` is merged on top of ``LLM_CONFIG``:

.. code-block:: python

   llm = create_llm("conf/gpt52.yaml", model="gpt-5.4", params={"seed": 7})
