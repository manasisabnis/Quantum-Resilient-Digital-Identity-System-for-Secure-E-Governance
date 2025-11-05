import { network } from "hardhat";

async function main() {
  console.log("Deploying DataHashStore contract...");

  const { ethers } = await network.connect({
    network: "ganache",
    chainType: "l1",
  });

  // Get the signer (using the first account from Ganache)
  const [deployer] = await ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());

  // Get the ContractFactory and Signers here.
  const DataHashStore = await ethers.getContractFactory("DataHashStore");

  // Start deployment, returning a promise that resolves to a contract object
  const dataHashStore = await DataHashStore.deploy();
  console.log("Contract deployment transaction sent...");

  // Wait for deployment to complete
  await dataHashStore.waitForDeployment();

  const contractAddress = await dataHashStore.getAddress();
  console.log("DataHashStore deployed to:", contractAddress);

  // Get the contract ABI
  const abi = DataHashStore.interface.format();
  console.log("Contract ABI:", JSON.stringify(abi, null, 2));

  // Example usage: Store a hash
  const id = "example_id";
  const hash = ethers.keccak256(ethers.toUtf8Bytes("example data"));
  console.log("Storing hash:", hash);

  const tx = await dataHashStore.storeHash(id, hash);
  await tx.wait();
  console.log("Hash stored successfully");

  // Verify the hash
  const isValid = await dataHashStore.verifyHash(id, hash);
  console.log("Hash verification:", isValid);

  // Get the hash
  const retrievedHash = await dataHashStore.getHash(id);
  console.log("Retrieved hash:", retrievedHash);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });