"""AES-256-GCM helper utilities.

This module provides a small wrapper around
cryptography.hazmat.primitives.ciphers.aead.AESGCM to simplify
encryption and decryption using AES-256 GCM with automatic nonce
generation.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AES256GCM:
    """Wrapper for AES-GCM (256-bit key).

    Attributes:
        key (bytes): 32-byte AES key.
        aesgcm (AESGCM): AESGCM instance created from the key.
    """

    def __init__(self, key=None):
        """Create an AES256GCM instance.

        Args:
            key (bytes, optional): 32-byte key. If omitted, a random
                256-bit key is generated.
        """
        self.key = key or AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext, nonce=None, associated_data=None):
        """Encrypt plaintext using AES-GCM.

        If `nonce` is not provided a random 12-byte nonce will be generated.

        Args:
            plaintext (bytes): Data to encrypt.
            nonce (bytes, optional): 12-byte nonce.
            associated_data (bytes, optional): Additional authenticated data.

        Returns:
            tuple: (nonce, ciphertext) where ciphertext includes the
                authentication tag.
        """
        nonce = nonce or os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce, ciphertext

    def decrypt(self, nonce, ciphertext, associated_data=None):
        """Decrypt ciphertext using AES-GCM.

        Args:
            nonce (bytes): 12-byte nonce used during encryption.
            ciphertext (bytes): Ciphertext to decrypt (includes auth tag).
            associated_data (bytes, optional): Additional authenticated data.

        Returns:
            bytes: Decrypted plaintext.
        """
        return self.aesgcm.decrypt(nonce, ciphertext, associated_data)