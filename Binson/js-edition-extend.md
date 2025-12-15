# BinJson

The **extended edition/version** of the JavaScript **BinJSON** library with **WebSocket streaming support**, **improved error handling**, 
and **additional utilities** for both **Node.js** and **browser environments**.

---

## **1. `binjson.js` (Enhanced Core Library)**
```javascript
const msgpack = require('msgpack-lite');
const AJV = require('ajv');
const CryptoJS = require('crypto-js');
const zlib = require('zlib');
const fs = require('fs');
const { WebSocket } = require('ws'); // Node.js WebSocket

// For browsers, replace with:
// const WebSocket = window.WebSocket;

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
class NetworkError extends BinJSONError {}

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
    try {
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
    } catch (e) {
      throw new SecurityError(`Encryption failed: ${e.message}`);
    }
  }

  decrypt(data) {
    try {
      const iv = CryptoJS.enc.Hex.parse(data.slice(0, 32).toString('hex'));
      const encrypted = data.slice(32).toString('utf8');
      const decrypted = CryptoJS.AES.decrypt(
        encrypted,
        CryptoJS.enc.Utf8.parse(this.key),
        { iv }
      );
      return Buffer.from(decrypted.toString(CryptoJS.enc.Utf8));
    } catch (e) {
      throw new SecurityError(`Decryption failed: ${e.message}`);
    }
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

// --- WebSocket Streaming ---
class BinJSONWebSocket {
  constructor(url, binjsonInstance) {
    this.ws = new WebSocket(url);
    this.binjson = binjsonInstance;
    this.chunkBuffer = [];
    this.currentBinaryJSON = null;

    this.ws.onopen = () => console.log('WebSocket connected');
    this.ws.onclose = () => console.log('WebSocket disconnected');
    this.ws.onerror = (error) => {
      throw new NetworkError(`WebSocket error: ${error.message}`);
    };

    this.ws.onmessage = (event) => {
      const chunk = Buffer.from(event.data);
      this.chunkBuffer.push(chunk);

      // Assume the first chunk contains the header and metadata
      if (this.chunkBuffer.length === 1) {
        const header = this.chunkBuffer[0].slice(0, 6);
        const metadataLength = this.chunkBuffer[0].readUInt32BE(6);
        const metadata = msgpack.decode(
          this.chunkBuffer[0].slice(6, 6 + metadataLength)
        );
        this.currentBinaryJSON = new BinaryJSON(
          header,
          metadata,
          Buffer.concat(this.chunkBuffer).slice(6 + metadataLength)
        );
      } else {
        // Append to payload
        this.currentBinaryJSON.payload = Buffer.concat([
          this.currentBinaryJSON.payload,
          chunk,
        ]);
      }
    };
  }

  send(binaryJSON) {
    if (this.ws.readyState !== WebSocket.OPEN) {
      throw new NetworkError('WebSocket not connected');
    }

    const chunks = this.binjson.handler.process(
      Buffer.concat([
        binaryJSON.header,
        msgpack.encode(binaryJSON.metadata),
        binaryJSON.payload,
      ])
    );

    chunks.forEach((chunk) => {
      this.ws.send(chunk);
    });
  }

  getReceivedData() {
    if (!this.currentBinaryJSON) {
      throw new BinJSONError('No data received yet');
    }
    return this.binjson.deserialize(this.currentBinaryJSON);
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

  createWebSocket(url) {
    return new BinJSONWebSocket(url, this);
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
  const metadataLength = data.readUInt32BE(6);
  const metadata = msgpack.decode(data.slice(6, 6 + metadataLength));
  const payload = data.slice(6 + metadataLength);
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
    BinJSONWebSocket,
    saveToFile,
    loadFromFile,
    BinJSONError,
    SchemaError,
    SecurityError,
    NetworkError,
  };
} else {
  // Browser: Expose globally
  window.BinJSON = {
    BinJSON,
    BinaryJSON,
    SchemaValidator,
    SecurityManager,
    DataHandler,
    BinJSONWebSocket,
    BinJSONError,
    SchemaError,
    SecurityError,
    NetworkError,
  };
}
```

---

## **2. `websocket-example.js` (WebSocket Streaming Example)**
```javascript
const { BinJSON } = require('./binjson');

// --- Example Schema ---
const schema = {
  type: 'object',
  properties: {
    id: { type: 'integer' },
    name: { type: 'string' },
  },
  required: ['id', 'name'],
};

// --- Initialize BinJSON ---
const binjson = new BinJSON(schema, 'my_32byte_secret_key_here...');

// --- WebSocket Server (Node.js) ---
if (typeof WebSocket !== 'undefined') {
  const wss = new WebSocket.Server({ port: 8080 });

  wss.on('connection', (ws) => {
    console.log('Client connected');

    // Send data to client
    const data = { id: 1, name: 'Alice' };
    const binaryData = binjson.serialize(data, 1, true, true);
    const wsClient = binjson.createWebSocket('ws://localhost:8080');
    wsClient.ws = ws; // Replace WebSocket instance for server-side
    wsClient.send(binaryData);
  });
}

// --- WebSocket Client (Browser or Node.js) ---
function runWebSocketClient() {
  const wsUrl = 'ws://localhost:8080';
  const wsClient = binjson.createWebSocket(wsUrl);

  // Send data after connection
  wsClient.ws.onopen = () => {
    const data = { id: 2, name: 'Bob' };
    const binaryData = binjson.serialize(data, 1, true, true);
    wsClient.send(binaryData);
  };

  // Retrieve received data after a delay (for demo purposes)
  setTimeout(() => {
    try {
      const receivedData = wsClient.getReceivedData();
      console.log('Received data:', receivedData);
    } catch (e) {
      console.error('Error:', e.message);
    }
  }, 1000);
}

// Uncomment to run the WebSocket client example
// runWebSocketClient();
```

---

## **3. `example.js` (Updated Usage Example)**
```javascript
const { BinJSON, saveToFile, loadFromFile } = require('./binjson');

// --- Example Schema ---
const schema = {
  type: 'object',
  properties: {
    id: { type: 'integer' },
    name: { type: 'string' },
    age: { type: 'integer', minimum: 0 },
  },
  required: ['id', 'name'],
};

// --- Initialize BinJSON ---
const binjson = new BinJSON(schema, 'my_32byte_secret_key_here...');

// --- Serialize Data ---
const data = { id: 1, name: 'Alice', age: 30 };
const binaryData = binjson.serialize(data, 1, true, true);
console.log('Serialized data:', binaryData);

// --- Save to File (Node.js) ---
saveToFile(binaryData, 'data.bin');
console.log('Saved to data.bin');

// --- Load from File (Node.js) ---
const loadedData = loadFromFile('data.bin');

// --- Deserialize Data ---
const restoredData = binjson.deserialize(loadedData, true);
console.log('Restored data:', restoredData);

// --- Streaming Mode ---
binjson.setHandlerMode('stream', 512);
const streamData = binjson.serialize({ id: 2, name: 'Bob', age: 25 }, 1, true, false);
const chunks = binjson.handler.process(
  Buffer.concat([
    streamData.header,
    msgpack.encode(streamData.metadata),
    streamData.payload,
  ])
);
console.log(`Streaming in ${chunks.length} chunks`);

// --- WebSocket Example ---
// Uncomment to test WebSocket functionality
// runWebSocketClient();
```

---

## **4. Key Improvements**
| Feature               | Implementation                          |
|-----------------------|-----------------------------------------|
| **WebSocket Support** | Real-time binary JSON streaming.        |
| **Error Handling**    | Better exceptions for network/security.|
| **Chunked Transfer**  | Efficient large data streaming.         |
| **Browser Compatible**| Works in Node.js and browsers.          |

---

## **5. How to Use**
### **Node.js**
1. Install dependencies:
   ```bash
   npm install msgpack-lite ajv crypto-js zlib ws
   ```
2. Run examples:
   ```bash
   node example.js
   node websocket-example.js
   ```

### **Browser**
1. Include dependencies:
   ```html
   <script src="https://unpkg.com/msgpack-lite@0.1.26/dist/msgpack.min.js"></script>
   <script src="https://unpkg.com/crypto-js@4.1.1/crypto-js.js"></script>
   <script src="https://unpkg.com/ajv@8.11.0/dist/ajv.min.js"></script>
   <script src="binjson.js"></script>
   ```
2. Use globally:
   ```javascript
   const binjson = new BinJSON.BinJSON(schema, 'secret_key');
   ```

---

## **6. Future Enhancements**
- **Query Engine**: Add SQL-like queries for binary data.
- **IndexedDB Support**: Browser storage for BinJSON.
- **Performance Optimizations**: WebAssembly for faster encryption/compression.
- **React/Vue Plugins**: Easy integration with front-end frameworks.

---

> Note: This **enhanced edition/version** adds **WebSocket streaming**, **better error handling**, and **cross-environment support** (Node.js + browser).
