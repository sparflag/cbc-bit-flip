"""Shared helper used by every challenge container to fetch its flag material.

Reads ``SPARFLAG_SERVER`` + ``SPARFLAG_INSTANCE_TOKEN`` (legacy ``PICOCLONE_*``
aliases still accepted), calls the server for this instance's encoded blob, and
returns the material dict. The container embeds the blob; the plaintext flag is
recovered only by solving.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request


def _require_env(*names: str) -> str:
    """Return the first non-empty environment value among ``names``.

    Args:
        *names: Environment variable names to try, in preference order.

    Returns:
        The first non-empty value found.

    Raises:
        KeyError: If none of the named variables are set to a non-empty value.
    """
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    raise KeyError(names[0])


def fetch_material() -> dict:
    """Fetch encoded flag material for the current challenge instance.

    Returns:
        JSON object from ``GET /api/instances/{id}/material``.

    Raises:
        KeyError: When required Sparflag (or legacy) env vars are missing.
        urllib.error.URLError: When the material request fails.
    """
    server = _require_env("SPARFLAG_SERVER", "PICOCLONE_SERVER").rstrip("/")
    token = _require_env("SPARFLAG_INSTANCE_TOKEN", "PICOCLONE_INSTANCE_TOKEN")
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    instance_id = json.loads(base64.urlsafe_b64decode(payload))["instance_id"]
    req = urllib.request.Request(
        f"{server}/api/instances/{instance_id}/material",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    print(json.dumps(fetch_material()))
