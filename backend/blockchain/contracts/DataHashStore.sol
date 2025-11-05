// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataHashStore {
    mapping(string => bytes32) private hashes;

    event HashStored(string indexed id, bytes32 hash);

    function storeHash(string memory id, bytes32 hash) public {
        hashes[id] = hash;
        emit HashStored(id, hash);
    }

    function verifyHash(string memory id, bytes32 hash) public view returns (bool) {
        return hashes[id] == hash;
    }

    function getHash(string memory id) public view returns (bytes32) {
        return hashes[id];
    }
}