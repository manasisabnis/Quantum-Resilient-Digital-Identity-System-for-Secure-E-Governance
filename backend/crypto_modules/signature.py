"""Dilithium signature helper using the oqs bindings.

Normalizes a few differences across bindings: some return keys directly
from generate_keypair(), others expose export/import helpers. Dynamic
members of the oqs binding are used, so the ``no-member`` lint rule is
disabled for this module.
"""

import oqs  # type: ignore
from oqs_utils import normalize_gen_result, export_secret_if_missing

# Dynamic API; silence false positives from pylint about missing members.
# pylint: disable=no-member


class DilithiumSignature:
    """Wrapper for Dilithium signature operations.

    Provides generate_keypair(), sign() and verify() helpers that work with
    a variety of oqs binding behaviours.
    """

    def __init__(self, mechanism: str = "Dilithium3"):
        """Create a DilithiumSignature helper for the given mechanism."""
        self.mechanism = mechanism
        self.public_key = None
        self.private_key = None

    def generate_keypair(self):
        """Generate (public, private) keypair.

        Returns (pub, priv) where priv may be None if the binding does not
        expose it directly.
        """
        sig = oqs.Signature(self.mechanism)
        gen = sig.generate_keypair()
        pub, priv = normalize_gen_result(gen)

        # try to export secret key if not returned directly
        if priv is None:
            priv = export_secret_if_missing(sig)

        self.public_key = pub
        self.private_key = priv
        return pub, priv

    def sign(self, message: bytes):
        """Sign a message using an attached private key.

        The implementation first attempts to attach the private key to the
        signature instance (via an attribute or import API). It then calls
        the sign function. Some bindings only provide a single-argument API
        that reads the secret from the instance.
        """
        if self.private_key is None:
            _msg = "No private key available; call generate_keypair()."
            raise ValueError(_msg)

        sig = oqs.Signature(self.mechanism)

    # Attach the private key to the Signature instance so single-arg
    # API can use it
        try:
            sig.secret_key = self.private_key
        except (AttributeError, TypeError) as exc:
            # fallback to import API if available
            if hasattr(sig, "import_secret_key"):
                try:
                    sig.import_secret_key(self.private_key)
                except (RuntimeError, TypeError, ValueError) as inner_exc:
                    _msg = "Unable to attach secret key to Signature instance"
                    raise ValueError(_msg) from inner_exc
            else:
                _msg = "Unable to attach secret key to Signature instance"
                raise ValueError(_msg) from exc

        # Call single-arg sign which reads sig.secret_key. Use getattr to avoid
        # static analysis issues about observed signatures on the dynamic API.
        sign_fn = getattr(sig, "sign")
        try:
            return sign_fn(message)
        except TypeError:
            # fallback: some bindings may accept the private key
            # as a second arg
            return sign_fn(message, self.private_key)

    def verify(
        self,
        message: bytes,
        signature: bytes,
        public_key: bytes,
    ) -> bool:
        """Verify a signature using an explicit public key.

        Returns True on success, False on verification failure or invalid
        input.
        """
        sig = oqs.Signature(self.mechanism)
        try:
            return sig.verify(message, signature, public_key)
        except (RuntimeError, TypeError, ValueError):
            return False