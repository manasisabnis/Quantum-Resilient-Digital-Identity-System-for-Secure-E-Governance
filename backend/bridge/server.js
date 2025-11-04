const http = require('http');
const fs = require('fs');
const path = require('path');

// Provide a robust `fetch` implementation that works on Node 18+ (global fetch)
// and falls back to dynamic import of node-fetch when needed. This avoids
// require() issues with ESM-only versions of node-fetch.
let fetchFn;
if (typeof globalThis.fetch === 'function') {
  fetchFn = globalThis.fetch.bind(globalThis);
} else {
  // late/dynamic import to handle ESM-only node-fetch versions
  fetchFn = async (...args) => {
    const mod = await import('node-fetch');
    // node-fetch exports the default function
    return mod.default(...args);
  };
}

// allow overriding with environment variable; default to 3001 to avoid collisions
const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3001;
const PY_BACKEND = process.env.PY_BACKEND || 'http://localhost:5000';

const mime = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain',
};

const server = http.createServer(async (req, res) => {
  const url = req.url === '/' ? '/index.html' : req.url;

  // Basic CORS handling: allow requests from any origin by default, or echo back the Origin
  const origin = req.headers.origin || '*';
  const setCorsHeaders = (extraHeaders = {}) => {
    const headers = {
      'Access-Control-Allow-Origin': origin,
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': req.headers['access-control-request-headers'] || 'Content-Type',
      'Access-Control-Max-Age': '86400',
      ...extraHeaders,
    };
    Object.entries(headers).forEach(([k, v]) => res.setHeader(k, v));
  };

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    setCorsHeaders();
    res.writeHead(204);
    res.end();
    return;
  }

  // Proxy registration requests to Python backend
  if (req.method === 'POST' && url === '/api/register') {
    try {
      let body = '';
      for await (const chunk of req) body += chunk;

      // Forward to Python backend
      const backendRes = await fetchFn(`${PY_BACKEND}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': req.headers['content-type'] || 'application/json' },
        body,
      });

      const text = await backendRes.text();
      // forward status and headers (and include CORS)
      setCorsHeaders({ 'Content-Type': backendRes.headers.get('content-type') || 'application/json' });
      res.writeHead(backendRes.status);
      res.end(text);
    } catch (err) {
      console.error('Proxy error:', err);
      setCorsHeaders({ 'Content-Type': 'application/json' });
      res.writeHead(502);
      res.end(JSON.stringify({ message: 'Proxy error', error: String(err) }));
    }
    return;
  }

  // Serve static files
  const filePath = path.join(__dirname, url.split('?')[0]);
  const resolvedBase = path.resolve(__dirname);
  const resolvedPath = path.resolve(filePath);
  // prevent directory traversal
  if (!resolvedPath.startsWith(resolvedBase)) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('Bad request');
    return;
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      setCorsHeaders();
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    setCorsHeaders();
    res.writeHead(200, { 'Content-Type': mime[ext] || 'application/octet-stream' });
    res.end(content);
  });
});

server.listen(PORT, () => {
  console.log(`Middle server running at http://localhost:${PORT}`);
  console.log('Serving files from', __dirname);
  console.log(`Proxying /api/register -> ${PY_BACKEND}/api/register`);
});

// graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down server...');
  server.close(() => process.exit(0));
});