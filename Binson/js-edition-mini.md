# **BinJSON for JavaScript (Browser & Node.js)**

BinJSON library, compatible with both **Node.js** and **browser environments**. It includes:
- Binary JSON serialization/deserialization (using `msgpack-lite`).
- Schema validation (using `ajv`).
- AES-256 encryption (using `crypto-js`).
- Batch/stream support.
- File I/O (Node.js only).

---

## **1. `binjson.js` (Core Library)**
```javascript
const msgpack = require('msgpack-lite');
const AJV = require('ajv');
const CryptoJS = require('crypto-js');
const zlib = require('zlib');
const fs = require('fs');

// --- Constants ---
const MAGIC_NUMBER = Buffer.from([0x42, 0x4A]); // "BJ" (use env for this)
const DEFAULT_SCHEMA_ID = 1;
const CHUNK_SIZE = 1024;

// --- Errors ---
class BinJSONError extends Error {
  constructor(message) {
    super(message);
    this.name = 'BinJSONError';
  }
}

class SchemaError extends BinJSONError {}
class SecurityError extends BinJSONError {}

// --- Core Classes ---
class BinaryJSON {
  constructor(header, metadata, payload) {
    this.header = header;
    this.metadata = metadata;
    this.payload = payload;
  }

  static fromDict(data, schemaId = DEFAULT_SCHEMA_ID, compress = true) {
    const metadata = {
      schema_id: schemaId,
      timestamp: Date.now(),
      compression: compress ? 'zlib' : 'none',
    };
    let payload = msgpack.encode(data);
    if (compress) {
      payload = zlib.deflateSync(payload);
    }
    const header = Buffer.concat([MAGIC_NUMBER, Buffer.alloc(4)]);
    header.writeUInt32BE(schemaId, 2);
    return new BinaryJSON(header, metadata, payload);
  }

  toDict() {
    let decompressed = this.payload;
    if (this.metadata.compression === 'zlib') {
      decompressed = zlib.inflateSync(this.payload);
    }
    return msgpack.decode(decompressed);
  }
}

class SchemaValidator {
  constructor(schema) {
    this.ajv = new AJV();
    this.validateFn = this.ajv.compile(schema);
  }

  validate(data) {
    if (!this.validateFn(data)) {
      throw new SchemaError(
        `Validation failed: ${this.ajv.errorsText(this.validateFn.errors)}`
      );
    }
    return true;
  }
}

class SecurityManager {
  constructor(key) {
    this.key = key || CryptoJS.lib.WordArray.random(32).toString();
  }

  encrypt(data) {
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(
      CryptoJS.lib.WordArray.create(data),
      CryptoJS.enc.Utf8.parse(this.key),
      { iv }
    );
    return Buffer.concat([
      Buffer.from(iv.toString(), 'hex'),
      Buffer.from(encrypted.toString(), 'utf8'),
    ]);
  }

  decrypt(data) {
    const iv = CryptoJS.enc.Hex.parse(data.slice(0, 32).toString('hex'));
    const encrypted = data.slice(32).toString('utf8');
    const decrypted = CryptoJS.AES.decrypt(
      encrypted,
      CryptoJS.enc.Utf8.parse(this.key),
      { iv }
    );
    return Buffer.from(decrypted.toString(CryptoJS.enc.Utf8));
  }

  sign(data) {
    return CryptoJS.HmacSHA256(data, this.key).toString();
  }
}

class DataHandler {
  constructor(mode = 'batch', chunkSize = CHUNK_SIZE) {
    this.mode = mode;
    this.chunkSize = chunkSize;
  }

  process(data) {
    if (this.mode === 'batch') {
      return data;
    } else {
      const chunks = [];
      for (let i = 0; i < data.length; i += this.chunkSize) {
        chunks.push(data.slice(i, i + this.chunkSize));
      }
      return chunks;
    }
  }
}

class BinJSON {
  constructor(schema = null, securityKey = null) {
    this.schema = schema;
    this.validator = schema ? new SchemaValidator(schema) : null;
    this.security = new SecurityManager(securityKey);
    this.handler = new DataHandler();
  }

  serialize(data, schemaId = DEFAULT_SCHEMA_ID, compress = true, encrypt = false) {
    if (this.validator) {
      this.validator.validate(data);
    }
    const binaryJson = BinaryJSON.fromDict(data, schemaId, compress);
    if (encrypt) {
      binaryJson.payload = this.security.encrypt(binaryJson.payload);
    }
    return binaryJson;
  }

  deserialize(binaryJson, decrypt = false) {
    if (decrypt) {
      binaryJson.payload = this.security.decrypt(binaryJson.payload);
    }
    return binaryJson.toDict();
  }

  setHandlerMode(mode, chunkSize = CHUNK_SIZE) {
    this.handler.mode = mode;
    this.handler.chunkSize = chunkSize;
  }
}

// --- Utility Functions (Node.js only) ---
function saveToFile(binaryJson, filepath) {
  const buffer = Buffer.concat([
    binaryJson.header,
    msgpack.encode(binaryJson.metadata),
    binaryJson.payload,
  ]);
  fs.writeFileSync(filepath, buffer);
}

function loadFromFile(filepath) {
  const data = fs.readFileSync(filepath);
  const header = data.slice(0, 6);
  const metadata = msgpack.decode(data.slice(6, 6 + data.readUInt32BE(6)));
  const payload = data.slice(6 + data.readUInt32BE(6));
  return new BinaryJSON(header, metadata, payload);
}

// --- Export for Node.js/Browser ---
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    BinJSON,
    BinaryJSON,
    SchemaValidator,
    SecurityManager,
    DataHandler,
    saveToFile,
    loadFromFile,
    BinJSONError,
    SchemaError,
    SecurityError,
  };
} else {
  // Browser: Expose globally
  window.BinJSON = {
    BinJSON,
    BinaryJSON,
    SchemaValidator,
    SecurityManager,
    DataHandler,
    BinJSONError,
    SchemaError,
    SecurityError,
  };
}
```

---

## **2. `example.js` (Usage)**
```javascript
const { BinJSON, saveToFile, loadFromFile } = require('./binjson');

// --- Example Schema ---
const schema = {
  type: 'object',
  properties: {
    id: { type: 'integer' },
    name: { type: 'string' },
  },
  required: ['id', 'name'],
};

// --- Initialize ---
const binjson = new BinJSON(schema, 'my_32byte_secret_key_here...');

// --- Serialize ---
const data = { id: 1, name: 'Alice' };
const binaryData = binjson.serialize(data, 1, true, true);
console.log('Serialized:', binaryData);

// --- Save to File (Node.js only) ---
saveToFile(binaryData, 'data.bin');

// --- Load from File (Node.js only) ---
const loadedData = loadFromFile('data.bin');

// --- Deserialize ---
const restoredData = binjson.deserialize(loadedData, true);
console.log('Restored:', restoredData);

// --- Streaming Example ---
binjson.setHandlerMode('stream', 512);
const streamData = binjson.serialize({ id: 2, name: 'Bob' }, 1, true);
const chunks = binjson.handler.process(streamData.payload);
console.log(`Streaming chunks: ${chunks.length}`);
```

---

## **3. `package.json` (Node.js Setup)**
```json
{
  "name": "binjson",
  "version": "0.1.0",
  "description": "Binary JSON library for JavaScript",
  "main": "binjson.js",
  "scripts": {
    "test": "node example.js"
  },
  "dependencies": {
    "msgpack-lite": "^0.1.26",
    "ajv": "^8.11.0",
    "crypto-js": "^4.1.1",
    "zlib": "^1.0.5"
  },
  "keywords": ["binary", "json", "serialization", "compression", "encryption"],
  "author": "lotuschain.org",
  "license": "MIT"
}
```

---

## **4. Key Features**
| Feature               | Implementation                          |
|-----------------------|-----------------------------------------|
| **Binary JSON**       | `msgpack-lite` for efficient encoding.  |
| **Schema Validation** | `ajv` for JSON Schema validation.       |
| **Security**          | `crypto-js` for AES-256 + HMAC.         |
| **Batch/Stream**      | Chunked processing with `zlib`.         |
| **File I/O**          | Node.js `fs` module.                    |

---

## **5. Browser Usage**
1. **Include via `<script>`**:
   ```html
   <script src="https://unpkg.com/msgpack-lite@0.1.26/dist/msgpack.min.js"></script>
   <script src="https://unpkg.com/crypto-js@4.1.1/crypto-js.js"></script>
   <script src="https://unpkg.com/ajv@8.11.0/dist/ajv.min.js"></script>
   <script src="binjson.js"></script>
   ```

2. **Use globally**:
   ```javascript
   const binjson = new BinJSON.BinJSON(schema, 'secret_key');
   ```

---

## **6. Notes**
- **Node.js**: Use `require('./binjson')`.
- **Browser**: Use `window.BinJSON`.
- **No File I/O in Browser**: Omit `saveToFile`/`loadFromFile`.
- **Future**: Publish to npm (`npm publish`).

---

JavaScript version of BinJSON!
