from __future__ import annotations

import os


def get_intapp_token() -> str:
    """
    Resolve the Intapp bearer token.

    Precedence:
    1) Environment variable `INTAPP_TOKEN` (recommended for CI and ephemeral sessions)
    2) Windows Credential Manager via `keyring` (recommended for local dev)
       - service: `intapp`
       - username: `INTAPP_TOKEN`
    """
    token = os.getenv("INTAPP_TOKEN")
    if token:
        return token

    try:
        import keyring  # type: ignore

        token = keyring.get_password("intapp", "INTAPP_TOKEN")
        if token:
            return token
    except ImportError as exc:
        raise RuntimeError(
            "Missing Intapp token. Set env var INTAPP_TOKEN, or install `keyring` and store it via:\n"
            "  pip install keyring\n"
            "  python -c \"import keyring; keyring.set_password('intapp','INTAPP_TOKEN','<token>')\""
        ) from exc
    except Exception:
        token = None

    raise RuntimeError(
        "Missing Intapp token. Set env var INTAPP_TOKEN or store it via:\n"
        "  python -c \"import keyring; keyring.set_password('intapp','INTAPP_TOKEN','<token>')\""
    )
