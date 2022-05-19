// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./SealedBidAuction.sol";

contract AuctionFactory{

    SealedBidAuction[] public sealedBidAuctionArray;
    mapping(address => uint256) auctionAddressToIndexInArray;

    function createSealedBidAuctionContract(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId, uint _revealTime, uint _winnerTime) public returns (uint256){

        SealedBidAuction auction = new SealedBidAuction(_minimumPriceHash, _nftContract, _tokenId, _revealTime, _winnerTime);
        sealedBidAuctionArray.push(auction);
        auctionAddressToIndexInArray[address(auction)] = sealedBidAuctionArray.length -1;
        auction.transferOwnership(msg.sender);
        return sealedBidAuctionArray.length -1; 
    }

}