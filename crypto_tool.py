#!/usr/bin/env python3
"""Encrypt/decrypt files with AES-256-GCM and calculate/verify SHA-256."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    print("Missing dependency: install with 'python -m pip install -r requirements.txt'.", file=sys.stderr)
    raise SystemExit(2)

MAGIC = b"ULK-AESGCM-1\n"
KEY_BYTES = 32
NONCE_BYTES = 12
CHUNK_SIZE = 1024 * 1024


class UserInputError(Exception):
    """An expected invalid-input or file error suitable for a concise CLI message."""


def read_key(path: Path) -> bytes:
    try:
        encoded = path.read_text(encoding="ascii").strip()
        key = base64.b64decode(encoded, validate=True)
    except FileNotFoundError as exc:
        raise UserInputError(f"Key file not found: {path}") from exc
    except (OSError, UnicodeError, ValueError) as exc:
        raise UserInputError(f"Cannot read a valid base64 key from: {path}") from exc
    if len(key) != KEY_BYTES:
        raise UserInputError(f"Invalid key length: expected {KEY_BYTES} decoded bytes.")
    return key


def generate_key(path: Path) -> None:
    if path.exists():
        raise UserInputError(f"Refusing to overwrite existing key file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL avoids replacing an existing file; restrict permissions on POSIX.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            stream.write(base64.b64encode(secrets.token_bytes(KEY_BYTES)).decode("ascii") + "\n")
    except OSError:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise
    print(f"Created a 256-bit key at {path}. Keep it outside the repository and back it up securely.")


def encrypt(source: Path, destination: Path, key_path: Path) -> None:
    if source.resolve() == destination.resolve():
        raise UserInputError("Input and output paths must be different.")
    try:
        data = source.read_bytes()
    except FileNotFoundError as exc:
        raise UserInputError(f"Input file not found: {source}") from exc
    except OSError as exc:
        raise UserInputError(f"Cannot read input file: {exc}") from exc
    key = read_key(key_path)
    nonce = secrets.token_bytes(NONCE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, data, MAGIC)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as stream:
            stream.write(MAGIC + nonce + ciphertext)
    except FileExistsError as exc:
        raise UserInputError(f"Refusing to overwrite existing output: {destination}") from exc
    except OSError as exc:
        raise UserInputError(f"Cannot write encrypted output: {exc}") from exc
    print(f"Encrypted {source} -> {destination} (AES-256-GCM; authenticated ciphertext).")


def decrypt(source: Path, destination: Path, key_path: Path) -> None:
    if source.resolve() == destination.resolve():
        raise UserInputError("Input and output paths must be different.")
    try:
        blob = source.read_bytes()
    except FileNotFoundError as exc:
        raise UserInputError(f"Encrypted file not found: {source}") from exc
    except OSError as exc:
        raise UserInputError(f"Cannot read encrypted file: {exc}") from exc
    if len(blob) < len(MAGIC) + NONCE_BYTES + 16 or not blob.startswith(MAGIC):
        raise UserInputError("Invalid encrypted file format or truncated ciphertext.")
    key = read_key(key_path)
    nonce_start = len(MAGIC)
    nonce = blob[nonce_start:nonce_start + NONCE_BYTES]
    try:
        plaintext = AESGCM(key).decrypt(nonce, blob[nonce_start + NONCE_BYTES:], MAGIC)
    except InvalidTag as exc:
        raise UserInputError("Authentication failed: wrong key or encrypted file was changed.") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as stream:
            stream.write(plaintext)
    except FileExistsError as exc:
        raise UserInputError(f"Refusing to overwrite existing output: {destination}") from exc
    except OSError as exc:
        raise UserInputError(f"Cannot write decrypted output: {exc}") from exc
    print(f"Decrypted {source} -> {destination} (AES-GCM authentication passed).")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise UserInputError(f"File not found: {path}") from exc
    except OSError as exc:
        raise UserInputError(f"Cannot read file: {exc}") from exc
    return digest.hexdigest()


def hash_command(path: Path, output: Path | None) -> None:
    digest = sha256_file(path)
    record = {"algorithm": "SHA-256", "file": path.name, "digest": digest}
    text = json.dumps(record, indent=2) + "\n"
    if output:
        try:
            with output.open("x", encoding="utf-8") as stream:
                stream.write(text)
        except FileExistsError as exc:
            raise UserInputError(f"Refusing to overwrite hash record: {output}") from exc
        except OSError as exc:
            raise UserInputError(f"Cannot write hash record: {exc}") from exc
        print(f"SHA-256 record saved to {output}.")
    else:
        print(text, end="")


def verify_hash(path: Path, record_path: Path) -> None:
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        expected = record["digest"]
        algorithm = record["algorithm"]
    except FileNotFoundError as exc:
        raise UserInputError(f"Hash record not found: {record_path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise UserInputError("Invalid hash record; expected JSON with algorithm and digest fields.") from exc
    if algorithm != "SHA-256" or not isinstance(expected, str) or len(expected) != 64:
        raise UserInputError("Invalid hash record: expected a 64-character SHA-256 digest.")
    if any(c not in "0123456789abcdefABCDEF" for c in expected):
        raise UserInputError("Invalid hash record: digest must contain hexadecimal characters.")
    actual = sha256_file(path)
    if secrets.compare_digest(actual.lower(), expected.lower()):
        print(f"MATCH: {path} is unchanged relative to {record_path}.")
    else:
        print(f"MISMATCH: {path} differs from the SHA-256 baseline in {record_path}.")
        raise SystemExit(1)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    p = commands.add_parser("keygen", help="Create a key at a path outside the repository")
    p.add_argument("--key", type=Path, required=True)
    p = commands.add_parser("encrypt", help="Encrypt a file with AES-256-GCM")
    p.add_argument("input", type=Path); p.add_argument("output", type=Path); p.add_argument("--key", type=Path, required=True)
    p = commands.add_parser("decrypt", help="Decrypt and authenticate a file")
    p.add_argument("input", type=Path); p.add_argument("output", type=Path); p.add_argument("--key", type=Path, required=True)
    p = commands.add_parser("hash", help="Calculate SHA-256; optionally save a baseline JSON record")
    p.add_argument("input", type=Path); p.add_argument("--out", type=Path)
    p = commands.add_parser("verify", help="Compare a file's SHA-256 with a baseline JSON record")
    p.add_argument("input", type=Path); p.add_argument("record", type=Path)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "keygen": generate_key(args.key)
        elif args.command == "encrypt": encrypt(args.input, args.output, args.key)
        elif args.command == "decrypt": decrypt(args.input, args.output, args.key)
        elif args.command == "hash": hash_command(args.input, args.out)
        elif args.command == "verify": verify_hash(args.input, args.record)
    except UserInputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
