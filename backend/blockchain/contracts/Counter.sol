// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract Counter {
  uint public x;
  bytes32 public storedHash;

  event Increment(uint by);
  event HashStored(bytes32 hash);

  function inc() public {
    x++;
    emit Increment(1);
  }

  function incBy(uint by) public {
    require(by > 0, "incBy: increment should be positive");
    x += by;
    emit Increment(by);
  }

  function storeHash(bytes32 hash) public {
    storedHash = hash;
    emit HashStored(hash);
  }
}
