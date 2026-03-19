<<<<<<< HEAD

=======
>>>>>>> bharath/development
"""Kyber (KEM) helper using the oqs bindings.

This module provides a small wrapper around the OQS KEM API to normalize
different oqs binding behaviours (some return keys directly, some expose
them via instance attributes or export functions).

Note: the `oqs` package uses dynamic members; we disable the ``no-member``
warning for this module so pylint doesn't report false positives.
"""

import oqs  # type: ignore
from oqs_utils import normalize_gen_result, export_secret_if_missing

# Pylint complains about dynamic members in the oqs binding; these are false
# positives because the library exposes attributes at runtime.
# pylint: disable=no-member


class KyberKeyExchange:
    """Wrapper for a post-quantum KEM (Kyber).

    The class stores the last generated/loaded public and private key and
    provides convenience methods to generate keypairs, encapsulate and
    decapsulate while normalizing a few binding differences.
    """

    def __init__(self, mechanism: str = "Kyber768"):
        """Create a KyberKeyExchange for a given mechanism.

        Args:
            mechanism: The OQS mechanism name to use (e.g. "Kyber768").
        """
        self.mechanism = mechanism
        self.public_key = None
        self.private_key = None

    def generate_keypair(self):
        """Generate a KEM keypair.

        Returns:
            tuple: (public_key: bytes, private_key: bytes|None)
        """
        kem = oqs.KeyEncapsulation(self.mechanism)
        gen = kem.generate_keypair()

        # Normalize returned values (some bindings return pub only).
        pub, priv = normalize_gen_result(gen)

        # Try to get secret key from kem instance if not returned directly
        if priv is None:
            priv = export_secret_if_missing(kem)

        self.public_key = pub
        self.private_key = priv
        return pub, priv

    def encapsulate(self, peer_public_key: bytes):
        """Encapsulate to a peer public key.

        Returns a tuple (ciphertext, shared_secret) when available. Some
        bindings return (ciphertext, shared) while others only return the
        ciphertext and expose the shared secret on the instance.
        """
        kem = oqs.KeyEncapsulation(self.mechanism)
        res = kem.encap_secret(peer_public_key)
        if isinstance(res, (tuple, list)):
            return res[0], res[1]

    # fallback: some bindings return only ciphertext but store
    # shared secret on the kem instance
        shared = None
        if hasattr(kem, "shared_secret") and kem.shared_secret is not None:
            shared = kem.shared_secret
        elif hasattr(kem, "export_shared_secret"):
            try:
                shared = kem.export_shared_secret()
            except (RuntimeError, TypeError, ValueError):
                shared = None
        return res, shared

    def decapsulate(self, ciphertext: bytes):
        """Decapsulate a ciphertext and return the shared secret.

        The method attempts to attach the stored private key to the KEM
        instance using the most appropriate API the binding provides.
        """
        kem = oqs.KeyEncapsulation(self.mechanism)

        if self.private_key is None:
            _msg = "No private key available; call generate_keypair()."
            raise ValueError(_msg)

    # attach the private key to the kem instance so decap_secret()
    # can use it
        try:
            kem.secret_key = self.private_key
        except (AttributeError, TypeError) as exc:
            # if assignment fails, try import style if available
            if hasattr(kem, "import_secret_key"):
                try:
                    kem.import_secret_key(self.private_key)
                except (RuntimeError, TypeError, ValueError) as inner_exc:
                    _msg = "Unable to attach secret key to KEM instance"
                    raise ValueError(_msg) from inner_exc
            else:
                _msg = "Unable to attach secret key to KEM instance"
                raise ValueError(_msg) from exc

        # use the single-arg API which reads kem.secret_key
        try:
            return kem.decap_secret(ciphertext)
        except (RuntimeError, TypeError, ValueError) as exc:
            raise RuntimeError("decap_secret failed") from exc
