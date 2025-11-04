"""Interactive CLI for credential creation and verification using
post-quantum primitives (KEM + AEAD + signatures).

Provides a simple register/login flow that demonstrates Kyber key
encapsulation, AES-256-GCM encryption, and Dilithium signatures.
"""

import sys
import re
import base64
import json
import getpass
from pathlib import Path
import binascii

# third-party imports
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# local application imports
from key_exchange import KyberKeyExchange
from encryption import AES256GCM
from signature import DilithiumSignature


def b64_encode(b: bytes) -> str:
    """Return base64 (ASCII) encoding of bytes.

    Args:
        b: bytes to encode

    Returns:
        ASCII string of base64 data.
    """
    return base64.b64encode(b).decode("ascii")


def b64_decode(s: str) -> bytes:
    """Decode a base64-encoded string to bytes."""
    return base64.b64decode(s)


def write_binary_b64(path: Path, data: bytes):
    """Write binary data to `path` as base64 text (UTF-8)."""
    path.write_text(b64_encode(data), encoding="utf-8")


def read_binary_b64(path: Path) -> bytes:
    """Read bytes from a file that may be base64-encoded text or raw bytes.

    The function first attempts to read the file as text and base64-decode
    it; if that fails it falls back to reading raw bytes.
    """
    txt = path.read_text(encoding="utf-8")
    try:
        return b64_decode(txt)
    except (binascii.Error, ValueError, TypeError):
        # base64 decoding can raise binascii.Error or TypeError
        # for invalid input
        return path.read_bytes()


def derive_aes_key(
    shared_secret: bytes,
    info: bytes = b"quantum-aegis",
) -> bytes:
    """Derive a 32-byte AES key from a shared secret using HKDF-SHA3-256."""
    hkdf = HKDF(
        length=32, salt=None, info=info, algorithm=hashes.SHA3_256()
    )
    return hkdf.derive(shared_secret)


def canonical_bytes_for_sig(obj: dict) -> bytes:
    """Return canonical JSON bytes for signing (omits signature fields)."""
    filtered = {
        k: v
        for k, v in obj.items()
        if k not in ("signature", "signer_pub")
    }
    return json.dumps(filtered, sort_keys=True, separators=(",", ":")).encode()


def resolve_encrypted_path(name: str) -> Path:
    """Resolve a likely path for an encrypted credential file.

    Tries the given name and a couple of standard directories.
    """
    p = Path(name)
    if p.exists():
        return p
    for d in (Path("Credentials"), Path("Encrypted")):
        cand = d / name
        if cand.exists():
            return cand
        cand2 = d / (name if name.endswith(".enc") else (name + ".enc"))
        if cand2.exists():
            return cand2
    cand_local = Path(name if name.endswith(".enc") else (name + ".enc"))
    if cand_local.exists():
        return cand_local
    return p


def sanitize_prefix(s: str) -> str:
    """Return a filesystem-safe prefix derived from an identifier (email).

    Lowercases and replaces unsafe characters.
    """
    s = s.lower().strip()
    # use local-part and domain with safe chars
    s = re.sub(r"[^a-z0-9@.+-_]", "_", s)
    s = s.replace("@", "_at_")
    s = s.replace(".", "_")
    return s[:64]


def ensure_dirs():
    """Create required directories if missing."""
    Path("Keys").mkdir(parents=True, exist_ok=True)
    Path("Credentials").mkdir(parents=True, exist_ok=True)


def _generate_kem_keys(prefix: str):
    """Generate a KEM keypair and store them under `Keys/`.

    Returns (pub, priv).
    """
    kem = KyberKeyExchange()
    pub, priv = kem.generate_keypair()
    kem_pub_path = Path("Keys") / (prefix + ".kem.pub")
    kem_priv_path = Path("Keys") / (prefix + ".kem.priv")
    write_binary_b64(kem_pub_path, pub)
    write_binary_b64(kem_priv_path, priv if priv is not None else b"")
    print(f"Generated KEM keys -> {kem_pub_path}, {kem_priv_path}")
    return pub, priv


def _generate_sig_keys(prefix: str):
    """Generate a Dilithium keypair and store them under `Keys/`.

    Returns (pub, priv).
    """
    sig = DilithiumSignature()
    spub, spriv = sig.generate_keypair()
    sig_pub_path = Path("Keys") / (prefix + ".sig.pub")
    sig_priv_path = Path("Keys") / (prefix + ".sig.priv")
    write_binary_b64(sig_pub_path, spub)
    write_binary_b64(sig_priv_path, spriv if spriv is not None else b"")
    if spriv is None:
        print(
            "Warning: Dilithium private key not exported; "
            "signing will not work."
        )
    else:
        print(f"Generated Dilithium keys -> {sig_pub_path}, {sig_priv_path}")
    return spub, spriv


def _create_envelope_and_store(ctx: dict):  # pylint: disable=too-many-locals
    """Build the credential envelope from ``ctx`` and store it.

    The context dictionary should contain: ``encapsulated``, ``shared``,
    ``email``, ``username``, ``password``, optional ``spriv``/``spub`` and
    ``mechanism``.
    """
    encapsulated = ctx["encapsulated"]
    shared = ctx["shared"]
    email = ctx["email"]
    username = ctx["username"]
    password = ctx["password"]
    spriv = ctx.get("spriv")
    spub = ctx.get("spub")
    mechanism = ctx.get("mechanism", "Kyber768")

    aes_key = derive_aes_key(shared, info=email.encode())
    aes = AES256GCM(aes_key)
    creds = json.dumps(
        {"username": username, "email": email, "password": password}
    )
    creds_b = creds.encode()
    nonce, ciphertext = aes.encrypt(creds_b)

    envelope = {
        "type": "credential",
        "alg": f"{mechanism}+AES-256-GCM",
        "encapsulated_key": b64_encode(encapsulated),
        "nonce": b64_encode(nonce),
        "ciphertext": b64_encode(ciphertext),
        "info": email,
        "user": username,
    }

    # Sign if private key available
    if spriv is not None:
        signer = DilithiumSignature()
        signer.public_key = spub
        signer.private_key = spriv
        msg = canonical_bytes_for_sig(envelope)
        try:
            signature = signer.sign(msg)
            envelope["signature"] = b64_encode(signature)
            envelope["signer_pub"] = b64_encode(spub)
            print("Envelope signed with Dilithium key.")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print("Signing failed:", exc)

    out_path = Path("Credentials") / (sanitize_prefix(email) + ".enc")
    out_path.write_text(json.dumps(envelope), encoding="utf-8")
    print(f"Credential envelope written to {out_path}")


def _verify_env_signature(env: dict) -> bool:
    """Verify envelope signature if present.

    Returns True if signature is absent or valid; False otherwise (and
    prints diagnostic messages).
    """
    sig_b64 = env.get("signature")
    if not sig_b64:
        return True
    signer_pub_b64 = env.get("signer_pub")
    if not signer_pub_b64:
        print("Envelope signature present but no signer_pub; abort.")
        return False
    signature = b64_decode(sig_b64)
    signer_pub = b64_decode(signer_pub_b64)
    verifier = DilithiumSignature()
    try:
        ok = verifier.verify(
            canonical_bytes_for_sig(env), signature, signer_pub
        )
    except Exception:  # pylint: disable=broad-exception-caught
        ok = False
    if not ok:
        print("Signature verification failed; abort.")
    return ok


def _decrypt_envelope_with_priv(priv: bytes, env: dict) -> dict | None:
    """Decapsulate and decrypt envelope using provided private key.

    Returns a dict of credentials on success or None on failure.
    """
    encapsulated = b64_decode(env["encapsulated_key"])
    nonce = b64_decode(env["nonce"])
    ciphertext = b64_decode(env["ciphertext"])
    info = env.get("info", "")

    kem = KyberKeyExchange()
    kem.private_key = priv
    try:
        shared = kem.decapsulate(encapsulated)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print("Decapsulation failed:", exc)
        return None

    info_bytes = info.encode() if isinstance(info, str) else info
    aes_key = derive_aes_key(shared, info=info_bytes)
    aes = AES256GCM(aes_key)
    try:
        plaintext = aes.decrypt(nonce, ciphertext)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print("Decryption failed:", exc)
        return None

    try:
        creds = json.loads(plaintext.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Decrypted payload invalid.")
        return None

    return creds


def interactive_register():
    """Interactive registration flow.

    Create keys and write a credential envelope for a new user. Uses
    helper functions to keep the function small and testable.
    """
    print("== Register (create credential + keys) ==")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ").strip()

    if not email:
        print("Email required.")
        return

    ensure_dirs()
    prefix = sanitize_prefix(email)

    pub, _ = _generate_kem_keys(prefix)
    spub, spriv = _generate_sig_keys(prefix)

    kem_enc = KyberKeyExchange()
    encapsulated, shared = kem_enc.encapsulate(pub)
    if shared is None:
        print("Error: KEM did not return shared secret; aborting.")
        return

    # Build and store the envelope using a helper to keep this function small
    ctx = {
        "encapsulated": encapsulated,
        "shared": shared,
        "email": email,
        "username": username,
        "password": password,
        "spriv": spriv,
        "spub": spub,
        "mechanism": kem_enc.mechanism,
    }
    _create_envelope_and_store(ctx)


def interactive_login():
    """Interactive login: verify signature, decapsulate and decrypt.

    Decrypt stored credentials and verify a provided password.
    """
    print("== Login (decrypt & verify) ==")
    email = input("Email: ").strip()
    password_try = getpass.getpass("Password: ").strip()

    if not email:
        print("Email required.")
        return

    env_path = resolve_encrypted_path(sanitize_prefix(email) + ".enc")
    if not env_path.exists():
        print("Credential not found for that email.")
        return

    env = json.loads(env_path.read_text(encoding="utf-8"))

    # verify signature if present
    if not _verify_env_signature(env):
        return

    # load KEM private key corresponding to this email and attempt decryption
    priv_path = Path("Keys") / (sanitize_prefix(email) + ".kem.priv")
    if not priv_path.exists():
        print("Private key not found for this account; cannot decrypt.")
        return

    priv = read_binary_b64(priv_path)
    creds = _decrypt_envelope_with_priv(priv, env)
    if creds is None:
        return

    stored_password = creds.get("password")
    if stored_password == password_try:
        print("Login successful.")
        print(f"Welcome, {creds.get('username')} ({creds.get('email')})")
    else:
        print("Invalid password.")


def interactive_loop():
    """Run the interactive CLI loop (register/login/exit).

    Keeps prompting the user for commands and dispatches to helper
    functions. This function intentionally handles broad exceptions at
    the top level to keep the CLI robust.
    """
    while True:
        print("\nChoose an action:")
        print("  1) Register")
        print("  2) Login")
        print("  3) Exit")
        choice = input("Select 1/2/3: ").strip()
        if choice in ("1", "register", "r"):
            try:
                interactive_register()
            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Error during register:", e)
        elif choice in ("2", "login", "l"):
            try:
                interactive_login()
            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Error during login:", e)
        elif choice in ("3", "exit", "q"):
            print("Exiting.")
            return
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    # When run without extra arguments, use interactive mode
    if len(sys.argv) == 1:
        interactive_loop()
    else:
        print(
            "This script now runs interactively. Run without args "
            "(python main.py)."
        )
