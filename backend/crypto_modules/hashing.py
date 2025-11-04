"""SHA3-256 hashing utilities.

Provides helpers to compute SHA3-256 digests in raw bytes and
hexadecimal form using the maintained ``cryptography`` library. This
replaces older, deprecated pycrypto usages to avoid security tooling
warnings.
"""

from cryptography.hazmat.primitives import hashes


class SHA3Hash:
    """Helper for SHA3-256 hashing.

    Provides two static helpers:
    - hash(data) -> bytes: returns raw digest bytes
    - hexdigest(data) -> str: returns hex-encoded digest
    """

    @staticmethod
    def hash(data: bytes) -> bytes:
        """Return the raw SHA3-256 digest for the given data.

        Args:
            data (bytes): Input data to hash.

        Returns:
            bytes: 32-byte SHA3-256 digest.
        """
        digest = hashes.Hash(hashes.SHA3_256())
        digest.update(data)
        return digest.finalize()

    @staticmethod
    def hexdigest(data: bytes) -> str:
        """Return the SHA3-256 digest as a hexadecimal string.

        Args:
            data (bytes): Input data to hash.

        Returns:
            str: Hexadecimal representation of the digest.
        """
        return SHA3Hash.hash(data).hex()
