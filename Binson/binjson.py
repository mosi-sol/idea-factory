# binjson.py
# Core Library
import json
import time
import zstandard as zstd
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Union, List
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
import msgpack

# --- Constants ---
MAGIC_NUMBER = b"\x42\x4A"  # "BJ" for BinaryJSON (use env for this)
DEFAULT_SCHEMA_ID = 1
CHUNK_SIZE = 1024  # For streaming

# --- Exceptions ---
class BinJSONError(Exception):
    pass

class SchemaError(BinJSONError):
    pass

class SecurityError(BinJSONError):
    pass

# --- Core Classes ---
@dataclass
class BinaryJSON:
    header: bytes
    metadata: Dict[str, Any]
    payload: bytes

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        schema_id: int = DEFAULT_SCHEMA_ID,
        compress: bool = True,
    ) -> "BinaryJSON":
        metadata = {
            "schema_id": schema_id,
            "timestamp": int(time.time()),
            "compression": "zstd" if compress else "none",
        }
        payload = msgpack.packb(data, use_bin_type=True)
        if compress:
            compressor = zstd.ZstdCompressor()
            payload = compressor.compress(payload)
        header = MAGIC_NUMBER + schema_id.to_bytes(4, "big")
        return cls(header=header, metadata=metadata, payload=payload)

    def to_dict(self) -> Dict[str, Any]:
        decompressor = zstd.ZstdDecompressor()
        try:
            decompressed = decompressor.decompress(self.payload)
        except:
            decompressed = self.payload  # Not compressed
        return msgpack.unpackb(decompressed, raw=False)

@dataclass
class SchemaValidator:
    schema: Dict[str, Any]

    def validate(self, data: Dict[str, Any]) -> bool:
        try:
            from jsonschema import validate
            validate(instance=data, schema=self.schema)
            return True
        except Exception as e:
            raise SchemaError(f"Validation failed: {e}")

@dataclass
class SecurityManager:
    key: bytes

    def __init__(self, key: Optional[bytes] = None):
        self.key = key or get_random_bytes(32)  # AES-256

    def encrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce + tag + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    def sign(self, data: bytes) -> bytes:
        hmac = HMAC.new(self.key, digestmod=SHA256)
        hmac.update(data)
        return hmac.digest()

@dataclass
class DataHandler:
    mode: str = "batch"  # "batch" or "stream"
    chunk_size: int = CHUNK_SIZE

    def process(self, data: bytes) -> Union[bytes, List[bytes]]:
        if self.mode == "batch":
            return data
        else:
            return [
                data[i : i + self.chunk_size]
                for i in range(0, len(data), self.chunk_size)
            ]

class BinJSON:
    def __init__(
        self,
        schema: Optional[Dict[str, Any]] = None,
        security_key: Optional[bytes] = None,
    ):
        self.schema = schema
        self.validator = SchemaValidator(schema) if schema else None
        self.security = SecurityManager(security_key)
        self.handler = DataHandler()

    def serialize(
        self,
        data: Dict[str, Any],
        schema_id: int = DEFAULT_SCHEMA_ID,
        compress: bool = True,
        encrypt: bool = False,
    ) -> BinaryJSON:
        if self.validator:
            self.validator.validate(data)
        binary_json = BinaryJSON.from_dict(data, schema_id, compress)
        if encrypt:
            binary_json.payload = self.security.encrypt(binary_json.payload)
        return binary_json

    def deserialize(
        self, binary_json: BinaryJSON, decrypt: bool = False
    ) -> Dict[str, Any]:
        if decrypt:
            binary_json.payload = self.security.decrypt(binary_json.payload)
        return binary_json.to_dict()

    def set_handler_mode(self, mode: str, chunk_size: int = CHUNK_SIZE):
        self.handler.mode = mode
        self.handler.chunk_size = chunk_size

# --- Utility Functions ---
def save_to_file(binary_json: BinaryJSON, filepath: str):
    with open(filepath, "wb") as f:
        f.write(binary_json.header + msgpack.packb(binary_json.metadata) + binary_json.payload)

def load_from_file(filepath: str) -> BinaryJSON:
    with open(filepath, "rb") as f:
        header = f.read(6)  # MAGIC (2) + schema_id (4)
        metadata = msgpack.unpackb(f.read(), raw=False)
        payload = f.read()
        return BinaryJSON(header=header, metadata=metadata, payload=payload)
