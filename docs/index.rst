LLM Interface
=============

A single Python interface to several LLM providers. Each model is described by one YAML file:
you load the file and call :meth:`~llm_base.BaseLLM.query`. The backend, the connection and the
request parameters all come from the file, so switching model means switching file, not code.

.. code-block:: python

   from llm_factory import create_llm

   llm = create_llm("conf/gpt52.yaml")
   ok, answer = llm.query("Summarise the plot of Hamlet in one sentence.")

.. toctree::
   :maxdepth: 2
   :caption: Guide

   usage
   configuration
   extending

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   backends

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
