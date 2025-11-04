"""Small utilities to normalize behaviours of dynamic `oqs` bindings.

Provides helpers used by KEM and signature wrappers to normalize the
different return shapes and export-style secret retrieval APIs across
oqs versions.
"""

from typing import Tuple, Optional


def normalize_gen_result(gen) -> Tuple[bytes, Optional[bytes]]:
    """Normalize a generate_keypair() result to (pub, priv).

    Some bindings return (pub, priv), others return only pub. This helper
    returns (pub, priv|None).
    """
    if isinstance(gen, (tuple, list)):
        if len(gen) >= 2:
            return gen[0], gen[1]
        return gen[0], None
    return gen, None


def export_secret_if_missing(instance) -> Optional[bytes]:
    """Attempt to obtain a secret key from an OQS-like instance.

    Checks common patterns: an attached ``secret_key`` attribute, or an
    ``export_secret_key()`` method. Returns the secret bytes or None.
    """
    # prefer direct attribute access if present
    sk = getattr(instance, "secret_key", None)
    if sk is not None:
        return sk
    if hasattr(instance, "export_secret_key"):
        try:
            return instance.export_secret_key()
        except (RuntimeError, TypeError, ValueError):
            return None
    return None
