import {network} from "hardhat";
import { expect } from "chai";



describe("DataHashStore", async function () {
  let ethers: any;
  let dataHashStore: any; 
  let deployer: any;

  const testId = "user-123";
  const testData = "This is some test data";
  let testHash: string;
  
  before(async function(){
    const { ethers : connectedEthers} = await network.connect({
      network: "ganache",
      chainType: "l1",
    });

    ethers = connectedEthers;
  })

  beforeEach(async function () {
    [deployer] = await ethers.getSigners();
    testHash = ethers.keccak256(ethers.toUtf8Bytes(testData));

    const DataHashStoreFactory = await ethers.getContractFactory("DataHashStore");
    dataHashStore = await DataHashStoreFactory.deploy();
    await dataHashStore.waitForDeployment();
  });
    

  it("Should deploy successfully", async function () {
    expect(await dataHashStore.getAddress()).to.not.be.null;
  });
  

  it("Should store a hash and emit an event", async function () {
    await expect(dataHashStore.storeHash(testId, testHash))
      .to.emit(dataHashStore, "HashStored")
      .withArgs(testId, testHash);
  });
  

  it("Should retrieve the correct hash using getHash", async function () {
    await dataHashStore.storeHash(testId, testHash);
    const retrievedHash = await dataHashStore.getHash(testId);
    expect(retrievedHash).to.equal(testHash);
  });
  

  it("Should return a zero hash for an unset ID", async function () {
    const retrievedHash = await dataHashStore.getHash("non-existent-id");
    expect(retrievedHash).to.equal(
      "0x0000000000000000000000000000000000000000000000000000000000000000"
    );
  });

  it("Should verify a stored hash correctly", async function () {
    await dataHashStore.storeHash(testId, testHash);
    const isCorrect = await dataHashStore.verifyHash(testId, testHash);
    expect(isCorrect).to.be.true;

    const incorrectHash = ethers.keccak256(ethers.toUtf8Bytes("wrong data"));
    const isIncorrect = await dataHashStore.verifyHash(testId, incorrectHash);
    expect(isIncorrect).to.be.false;
  });

  it("Should return false when verifying an unset ID", async function () {
    const isCorrect = await dataHashStore.verifyHash("non-existent-id", testHash);
    expect(isCorrect).to.be.false;
  });
});
