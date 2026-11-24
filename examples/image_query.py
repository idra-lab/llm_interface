"""Ask Azure GPT-5.2 to describe an image downloaded from the web.

The image is *The Great Wave off Kanagawa* by Hokusai, in the public domain, served by
Wikimedia Commons. It is kept in memory, so nothing is written to disk.

Needs ``AZURE_OPENAI_API_KEY`` and ``AZURE_OPENAI_ENDPOINT`` in the ``.env`` file at the
repository root. Run it from anywhere::

    python examples/image_query.py
"""

import sys
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

# Make the repository root importable when the script is run directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from llm_factory import create_llm  # noqa: E402

CONFIG_FILE = ROOT / "conf" / "azure_gpt52.yaml"
IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/"
    "Tsunami_by_hokusai_19th_century.jpg/960px-Tsunami_by_hokusai_19th_century.jpg"
)
QUESTION = "Describe this image in a short paragraph."


def download_image(url: str) -> Image.Image:
    """Download an image and open it with Pillow.

    Parameters
    ----------
    url : str
        Address of the image.

    Returns
    -------
    Image.Image
        The decoded image.
    """
    # Wikimedia refuses requests that carry no User-Agent.
    request = urllib.request.Request(url, headers={"User-Agent": "llm_interface-example/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return Image.open(BytesIO(response.read()))


def main() -> None:
    """Send the image with a question and print the description."""
    image = download_image(IMAGE_URL)
    llm = create_llm(CONFIG_FILE)

    # images= also accepts file paths, e.g. images=["photo.jpg"].
    ok, answer = llm.query(QUESTION, images=[image])
    if not ok:
        sys.exit("The request failed. Check the log above and the credentials in .env.")

    print(answer)
    print("\nToken usage:", llm.last_usage)


if __name__ == "__main__":
    main()
