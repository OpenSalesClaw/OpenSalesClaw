// Local shim: native DOMException is available in Node 18+
module.exports = globalThis.DOMException;
