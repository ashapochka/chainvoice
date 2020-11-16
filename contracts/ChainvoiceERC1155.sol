// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

contract ChainvoiceERC1155 is ERC1155 {
    uint256 public constant CVT = 0;

    constructor() public ERC1155(
        "https://softserveinc-demo-chainvoice.azurewebsites.net/api/token/{1}.json"
    ) {
        _mint(msg.sender, CVT, 10**18, "");
    }
}
