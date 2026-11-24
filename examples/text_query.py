"""Ask Azure GPT-5.2 a text-only question.

Needs ``AZURE_OPENAI_API_KEY`` and ``AZURE_OPENAI_ENDPOINT`` in the ``.env`` file at the
repository root. Run it from anywhere::

    python examples/text_query.py
"""

import sys
from pathlib import Path

# Make the repository root importable when the script is run directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llm_factory import create_llm  # noqa: E402

CONFIG_FILE = ROOT / "conf" / "azure_gpt52.yaml"
QUESTION = "Explain in three sentences what a large language model is."


def main() -> None:
    """Send one question to the model and print the answer."""
    llm = create_llm(CONFIG_FILE)

    ok, answer = llm.query(QUESTION)
    if not ok:
        sys.exit("The request failed. Check the log above and the credentials in .env.")

    print(answer)
    print("\nToken usage:", llm.last_usage)


if __name__ == "__main__":
    main()
