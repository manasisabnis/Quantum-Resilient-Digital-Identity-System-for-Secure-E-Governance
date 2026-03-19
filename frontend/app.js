const BASE_URL = "http://localhost:5000";

function log(message) {
  const logBox = document.getElementById("log");
  logBox.innerHTML += `> ${message}<br>`;
  logBox.scrollTop = logBox.scrollHeight;
}

async function runProcess() {
  const name = document.getElementById("name").value;
  const id = document.getElementById("id").value;

  log("Initializing process...");
  await delay(500);

  log("Hashing identity...");
  await delay(700);

  const res = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ name, id })
  });

  const data = await res.json();

  log(`Hash generated: ${data.hash}`);
  await delay(500);

  log("Applying quantum-safe encryption...");
  await delay(700);

  log(`Encrypted: ${data.encrypted}`);
  await delay(500);

  log("Sending to blockchain...");
  await delay(800);

  log(`Transaction ID: ${data.txHash}`);
  log("Process Complete");
}

function delay(ms) {
  return new Promise(res => setTimeout(res, ms));
}