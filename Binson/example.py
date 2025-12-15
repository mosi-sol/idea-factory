# example.py
from binjson import BinJSON, save_to_file, load_from_file

# --- Example Schema ---
schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
    },
    "required": ["id", "name"],
}

# --- Initialize ---
binjson = BinJSON(schema=schema, security_key=b"my_secret_key_32byteslong...")

# --- Serialize ---
data = {"id": 1, "name": "Alice", "age": 30}
binary_data = binjson.serialize(data, encrypt=True)
print(f"Serialized: {binary_data.header[:6]}... (payload: {len(binary_data.payload)} bytes)")

# --- Save to File ---
save_to_file(binary_data, "data.bin")

# --- Load from File ---
loaded_data = load_from_file("data.bin")

# --- Deserialize ---
restored_data = binjson.deserialize(loaded_data, decrypt=True)
print(f"Restored: {restored_data}")

# --- Streaming Example ---
binjson.set_handler_mode("stream", chunk_size=512)
streaming_data = binjson.serialize({"id": 2, "name": "Bob", "age": 25}, compress=True)
chunks = binjson.handler.process(streaming_data.payload)
print(f"Streaming chunks: {len(chunks)}")
