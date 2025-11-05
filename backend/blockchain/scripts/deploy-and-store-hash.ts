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

  // Deploy the Counter contract
  const Counter = await ethers.getContractFactory("Counter");
  const counter = await Counter.deploy();

  await counter.waitForDeployment();

  const counterAddress = await counter.getAddress();
  console.log("Counter deployed to:", counterAddress);

  // Generate a SHA3-256 hash (example: hash of "test data")
  const data = "test data";
  const hash = ethers.keccak256(ethers.toUtf8Bytes(data)); // Note: ethers uses keccak256, which is SHA3-256 equivalent for Ethereum
  console.log("SHA3-256 hash:", hash);

  // Store the hash in the contract
  const tx = await counter.storeHash(hash);
  await tx.wait();

  console.log("Hash stored on chain:", hash);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });