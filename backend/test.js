const { storeHash, getStoredHash } = require("./utils/blockchain_utils.js");

(async () => {
  const hash =
    "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

  const result = await storeHash(hash);
  console.log("Stored at:", result);

  const stored = await getStoredHash("test-id");
  console.log("On-chain hash:", stored);
})();
