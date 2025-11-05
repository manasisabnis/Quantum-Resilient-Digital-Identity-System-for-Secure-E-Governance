import { network } from "hardhat";

async function main() {
  const { ethers } = await network.connect({
    network: "ganache",
    chainType: "l1",
  });

  // Get the signer (using the first account from Ganache)
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

  // Deploy the DataHashStore contract
  const DataHashStore = await ethers.getContractFactory("DataHashStore");
  const dataHashStore = await DataHashStore.deploy();

  await dataHashStore.waitForDeployment();

  const dataHashStoreAddress = await dataHashStore.getAddress();
  console.log("DataHashStore deployed to:", dataHashStoreAddress);

  // Generate a SHA3-256 hash (example: hash of "test data")
  const data = "test data";
  const dataId = "user-doc-123"; // The ID for the hash
  const hash = ethers.keccak256(ethers.toUtf8Bytes(data)); 
  console.log(`SHA3-256 hash for '${data}':`, hash);

  // Store the hash in the contract
  const tx = await dataHashStore.storeHash(dataId, hash);
  await tx.wait();

  console.log(`Hash stored on chain for ID '${dataId}':`, hash);

  // --- Optional: Verify the hash ---
  const storedHash = await dataHashStore.getHash(dataId);
  console.log(`Retrieved hash from contract:`, storedHash);
  
  const isMatch = await dataHashStore.verifyHash(dataId, hash);
  console.log(`Verification successful:`, isMatch);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });