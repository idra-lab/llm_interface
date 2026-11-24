Adding a backend
================

Every backend subclasses :class:`llm_base.BaseLLM`. The base class already implements
:meth:`~llm_base.BaseLLM.from_config`, :meth:`~llm_base.BaseLLM.query` with retries, message
building and parameter merging. A new provider fills in the connection hooks only.

#. Create ``LLMMyProvider/LLMMyProvider.py`` with a class ``LLMMyProvider(BaseLLM)``.
#. Set :attr:`~llm_base.BaseLLM.PROVIDER`, and :attr:`~llm_base.BaseLLM.SUPPORTS_IMAGES` when
   the provider accepts images.
#. Implement the three abstract hooks:

   * :meth:`~llm_base.BaseLLM._create_client` -- build the SDK client or load the model.
   * :meth:`~llm_base.BaseLLM._send` -- send the message list, return the raw response.
   * :meth:`~llm_base.BaseLLM._extract_text` -- pull the answer out of the response.

#. Optionally override :meth:`~llm_base.BaseLLM._setup` to read provider keys from
   ``self.config``, :meth:`~llm_base.BaseLLM._extract_usage` for token counts and
   :meth:`~llm_base.BaseLLM.image_part` for images.
#. Register the slug in :data:`llm_factory.PROVIDER_ALIASES` and
   :data:`llm_factory.PROVIDER_MODULES`.

A minimal example:

.. code-block:: python

   from llm_base import BaseLLM


   class LLMMyProvider(BaseLLM):
       PROVIDER = "myprovider"

       def _setup(self):
           self.api_key_name = self.config.get("API_KEY_NAME") or "MYPROVIDER_API_KEY"

       def _create_client(self):
           import os
           from myprovider import Client
           return Client(api_key=os.environ[self.api_key_name])

       def _send(self, client, messages):
           return client.chat(model=self.model, messages=messages, **self.request_params())

       def _extract_text(self, response):
           return response.text
