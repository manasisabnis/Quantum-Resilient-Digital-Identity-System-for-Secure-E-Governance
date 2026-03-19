# Connection project — README

This project is a small demo that shows a Node "middle" server (static file serving + proxy) running on Windows and a Python backend on a Kali VM which performs credential creation and decryption using post-quantum primitives (KEM + AEAD + signatures).

Overview of what you have implemented
- `server.js` — Node static file server and proxy that forwards POST API calls to the Python backend. It supports configuration via:
  - environment variable `PY_BACKEND`
  - CLI flag `--py-backend=http://host:port`
  - optional `.env` file (if you install `dotenv`).
- `main.py` — Python CLI + small Flask HTTP API. I added programmatic `register_user()` and a minimal Flask app exposing:
  - `POST /api/register` — creates keys and a credential envelope (writes `Keys/` and `Credentials/` on the Kali host)
  - `POST /api/login` — accepts `{ email, password }`, decrypts the stored envelope using the KEM private key, verifies password and returns success or error JSON.
- `index.html` — simple frontend (served by the Node server) with two views: Register and Login. It POSTs to the middle Node server at `http://localhost:3001/api/...` which proxies the request to the Python backend.

Files changed/added
- `main.py` (edited) — added `register_user()` and Flask endpoints `/api/register` and `/api/login`.
- `server.js` (edited) — added optional `.env` support, `--py-backend` CLI flag parsing, and proxying for `/api/register` and `/api/login`.
- `index.html` (edited) — added Register/Login UI, client-side JS to call the middle server.
- `README.md` (this file) — usage and troubleshooting.

How to run (recommended setup)

1) On Kali (Python backend)

```bash
# open the project folder where `main.py` lives
cd ~/Tools/connection

# (optional) create and activate a venv
python3 -m venv venv
source venv/bin/activate

# install required Python packages
pip install --upgrade pip
pip install flask cryptography

# run as an HTTP API listening on all interfaces (useful if the host will access it)
export PY_HOST=0.0.0.0
export PY_PORT=5000
python3 main.py --http
```

Notes:
- The Flask dev server is fine for testing. The API will write generated files under `Keys/` and `Credentials/` on the Kali host.

2) On Windows (Node middle server)

```powershell
cd "C:\Users\bhara\PROJECT\WEB DEV\connection"

# Option A — pass the backend on the CLI
npx nodemon -- .\server.js --py-backend=http://<KALI_IP>:5000

# Option B — set the env var for your session
$env:PY_BACKEND = "http://<KALI_IP>:5000"
npx nodemon .\server.js

# Option C — use a .env file with PY_BACKEND=http://<KALI_IP>:5000 and install dotenv
npm install dotenv --save
npx nodemon .\server.js
```

Replace `<KALI_IP>` with the IP assigned to the Kali VM that is reachable from Windows (for example `192.168.0.162`). If your VM is NATed and you can't reach that IP, use port-forwarding or an SSH tunnel (see section below).

3) Open the web UI

Open a browser on Windows and visit `http://localhost:3001/`.
- Use the Register form to create a user. The Python backend will create keys and an encrypted credential file on the Kali machine.
- Use the Login form to decrypt and verify the credential using the stored private key (the decryption occurs on Kali).

Troubleshooting — networking
- If Node shows `Proxy error: TypeError: fetch failed` it means Node couldn't reach the Python backend. Verify:
  - The Python server is running and listening on the expected port on Kali: `ss -ltnp | grep 5000` (Kali).
  - From Windows, verify TCP reachability: `Test-NetConnection -ComputerName <KALI_IP> -Port 5000 -InformationLevel Detailed` (PowerShell).
  - Use the direct HTTP test from Windows to the Python server: `Invoke-RestMethod -Uri "http://<KALI_IP>:5000/api/register" -Method Post -Body $body -ContentType 'application/json'`.

If the host cannot reach the guest's NAT IP (e.g. `10.0.2.8`), do one of:
- Switch VM to Bridged networking (guest gets a LAN IP reachable from host). Then use that IP as `<KALI_IP>`.
- Add a NAT port-forward rule (host port 5000 -> guest 5000) in your hypervisor so Windows can access the service via `localhost:5000`.
- Create an SSH tunnel from Windows:
  `ssh -L 5000:localhost:5000 user@<KALI_IP> -N` and then point Node at `http://localhost:5000`.

Security notes
- This demo stores private keys and encrypted credentials on disk in the `Keys/` and `Credentials/` folders. This is fine for local testing but not for production.
- The Flask built-in server is not production-grade. For production, use a proper WSGI server and TLS.

Developer notes / next steps
- I added support for `--py-backend` and `.env` in `server.js` so you can configure the Python backend easily.
- You can add more endpoints to `main.py` (list users, delete credentials) but be careful with exposing private key information.
- If you want, I can add a small README section describing how to package this in Docker or how to add HTTPS.

Files written at runtime
- On the Kali VM: `Keys/<prefix>.kem.pub`, `Keys/<prefix>.kem.priv`, `Keys/<prefix>.sig.pub`, `Keys/<prefix>.sig.priv` (if signatures exported).
- Encrypted credential: `Credentials/<prefix>.enc` (JSON envelope).

If you want me to: I can add a short `README` section that shows the exact copy/paste commands for your current environment (I'll fill in `192.168.0.162` as Kali IP if you confirm), or I can add a small `Makefile`/PowerShell script to start both services. Tell me which and I'll add it.

---
Generated on: 2025-11-05
