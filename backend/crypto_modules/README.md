# ⚔️ Updated Version - Quantum Aegis: Quantum-Resilient Cryptographic Framework 

Quantum Aegis is an **Hybrid Cryptographic Demo** that combines classical and post-quantum primitives to demonstrate a **quantum-resistant secure communication flow**.  
It pairs **AES-256-GCM** for symmetric confidentiality, **SHA3-256** for hashing, and **PQC algorithms (Kyber for KEM, Dilithium for signatures)** for key exchange and authentication.

---

## 🔑 Highlights
- **Hybrid stack:** AES-256-GCM + Kyber (KEM) + Dilithium (signatures) + SHA3-256  
- **Post-quantum ready:** Resistant against both classical and quantum adversaries  
- **Modular design:** Small, well-segregated modules (`key_exchange.py`, `signature.py`, `encryption.py`, `hashing.py`)  
- **Developer-friendly:** Easy to run in a Python `venv` on Linux (recommended)  
- **Educational:** Great for demonstrating PQC integration into real-world protocols  

---

## 🏗️ Architecture Diagram

```text
               ⚔️ Quantum Aegis — Secure Flow

     ┌──────────────┐                            ┌──────────────┐
     │    Client    │                            │    Server    │
     └──────┬───────┘                            └──────┬───────┘
            │                                         │
            │     1. Kyber Key Exchange (KEM)         │
            │─────────────── Public Key ─────────────▶│
            │◀────────────── Ciphertext ───────────── │
            │                                         │
            │     Shared Secret (ss) established      │
            │                                         │
            │     2. Dilithium Signature              │
            │───────────── Signed Message ───────────▶│
            │◀──────────── Verification ───────────── │
            │                                         │
            │     3. AES-256-GCM Encryption           │
            │────────────── Encrypted Msg ───────────▶│
            │◀────────────── Encrypted Reply ──────── │
            │                                         │
            │     4. SHA3-256 Hashing (Integrity)     │
            │────────────── Hash Digest ─────────────▶│
            │                                         │
     ┌──────┴───────┐                            ┌──────┴───────┐
     │  Post-Quantum│                            │  Post-Quantum│
     │   Security   │                            │   Security   │
     └──────────────┘                            └──────────────┘
```

## 📂 Project Structure
<pre>
Quantum_Aegis/
├── demo.py                    # 🎯 Minimal demo runner<br>
├── main.py                    # 🚀 Application launcher (runs full hybrid PQC flow)<br>
├── key_exchange.py            # 🔑 Kyber KEM operations<br>
├── signature.py               # ✍️ Dilithium digital signatures<br>
├── encryption.py              # 🔒 AES-256-GCM encryption/decryption<br>
├── hashing.py                 # 🌀 SHA3-256 hashing helpers<br>
├── requirements.txt           # 📦 Python dependencies<br>
└── README.md                  # 📖 Project documentation<br>
</pre>

## ⚙️ Setup
   1. Install prerequisites (Linux, e.g. Ubuntu/Kali/Debian)
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip build-essential cmake git libssl-dev pkg-config
   ```
   2. Create & activate a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   3. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   If pip install oqs fails due to missing wheels, see the Optional: Build liboqs from source section below.

   4. Optional: Build liboqs from source
   Use this only if the oqs wheel is unavailable for your Python version/platform.

   ```bash
   git clone --branch main https://github.com/open-quantum-safe/liboqs.git
   cd liboqs
   cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
   cmake --build build -j"$(nproc)"
   sudo cmake --install build
   cd ..
   pip install oqs --no-binary oqs
   ```

   🚀 Run the Demo
   With your venv active:
   ```bash
   python3 main.py
   ```

   Expected:

   - Key exchange using Kyber
   - Digital signature with Dilithium
   - Symmetric encryption with AES-GCM
   - Hashing with SHA3-256
   - Console logs showing secure communication flow
   - You can modify `demo.py` to experiment with different messages or flows.

   ## Configuration
   You can control runtime behavior with environment variables.<br>
   Recommended variables:

   - `QA_LOG_LEVEL` — logging level (e.g., `INFO`, `DEBUG`, default: `INFO`)
   - `QA_OQS_PROVIDER` — (optional) which OQS provider/binding to use if the code supports multiple providers

   ## 🔒 Security Notes
   - This project is a demo and not production-ready.
   - Do not use for protecting real secrets.
   - Private keys must be kept out of source control (add to .gitignore).

   ## 👨‍💻 Maintainer
   Bharath Honakatti<br>
   🌐 **Portfolio:** [bharathhonakatti26.github.io](https://bharathhonakatti26.github.io/portfolio/)


   ## References
   - [Open Quantum Safe (liboqs)](https://github.com/open-quantum-safe/liboqs)
   - [NIST Post-Quantum Cryptography Project](https://csrc.nist.gov/projects/post-quantum-cryptography)

   ---

   Enjoy experimenting with Quantum Aegis.
