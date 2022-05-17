// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TimeOracle is Ownable {

    AggregatorV3Interface[] public timeFeed;
    mapping(address => uint256) public feedToArrayLocation;

    constructor() {
        //timeFeed.push(AggregatorV3Interface(0x8A753747A1Fa494EC906cE90E9f37563A8AF630e));
    }

    // We suppose the address is a pricefeed, if not tx will revert
    function addPriceFeed(address _newFeed) public onlyOwner{
        require(feedToArrayLocation[_newFeed] == 0, 'Pricefeed already in contract');
        //Agrega al final
        AggregatorV3Interface newFeed = AggregatorV3Interface(_newFeed);
        timeFeed.push(newFeed);
        feedToArrayLocation[_newFeed] = timeFeed.length;
    }

    function deletePriceFeed(address _feedToDelete) public onlyOwner{
        require(feedToArrayLocation[_feedToDelete] != 0, 'Pricefeed not in contract');
        uint256 index = feedToArrayLocation[_feedToDelete] - 1;
        feedToArrayLocation[_feedToDelete] = 0;
        timeFeed[index] = timeFeed[timeFeed.length-1];
        timeFeed.pop();
    }

    function getLatestTime() public view returns (uint) {
        uint sumOfTimes;
        uint256 i;
        uint timeStamp;
        for(i = 0; i < timeFeed.length; i++){
            timeStamp = 0;
            ( , , , timeStamp,) = timeFeed[i].latestRoundData();
            sumOfTimes = sumOfTimes + timeStamp;
        }
        return (sumOfTimes + (sumOfTimes % timeFeed.length))/timeFeed.length;
    }

    function getLength() public view returns (uint){
        return timeFeed.length; 
    }
}