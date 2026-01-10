// Placeholder for blockchain team
const { ethers } = require("ethers");
const path = require("path");
require("dotenv").config({
  path: require("path").join(__dirname, "..", "blockchain", ".env"),
});


/**
 * 1. Connect to Ganache RPC
 */
const provider = new ethers.JsonRpcProvider(
  process.env.GANACHE_RPC_URL|| "http://127.0.0.1:8545"
);

/**
 * 2. Create signer (Ganache account)
 */
if (!process.env.GANACHE_PRIVATE_KEY) {
  throw new Error("GANACHE_PRIVATE_KEY not set in environment");
}
const signer = new ethers.Wallet(process.env.GANACHE_PRIVATE_KEY, provider);

/**
 * 3. Load contract ABI
 */
const contractArtifactPath = path.join(
  __dirname,
  "..",
  "blockchain",
  "artifacts",
  "contracts",
  "DataHashStore.sol",
  "DataHashStore.json"
);


const contractArtifact = require(contractArtifactPath);
const contractABI = contractArtifact.abi;

/**
 * 4. Load deployed contract address
 */
if (!process.env.CONTRACT_ADDRESS) {
  throw new Error("CONTRACT_ADDRESS not set in environment");
}
const contractAddress = process.env.CONTRACT_ADDRESS;

/**
 * 5. Create contract instance
 */
const contract = new ethers.Contract(
  contractAddress,
  contractABI,
  signer
);

/**
 * ===============================
 * EXPORTED BLOCKCHAIN FUNCTIONS
 * ===============================
 */

/**
 * Store SHA-256 hash on blockchain
 * @param {string} hashHex - 0x-prefixed 32-byte hex string
 */
async function storeHash(hashHex) {
  if (!hashHex || !hashHex.startsWith("0x") || hashHex.length !== 66) {
    throw new Error("Invalid bytes32 hash format");
  }

  const tx = await contract.storeHash("test-id", hashHex);
  const receipt = await tx.wait();

  return {
    txHash: receipt.hash,
    blockNumber: receipt.blockNumber,
  };
}

/**
 * Read stored hash from blockchain
 */
async function getStoredHash(id) {
  const hash = await contract.getHash(id);
  return hash;
}

module.exports = {
  storeHash,
  getStoredHash,
};
