// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

contract SealedBidAuction is Ownable, IERC721Receiver {


    address[] public players; // Para poder regresar x a los que no ganan

    mapping(address => uint256) public accountToAmount;
    mapping(address => bytes32) public accountToHash;
    mapping(address => uint256) public accountToOffer;

    address public winner;
    uint256 public amount;
    bytes32 public minimumPriceHash;
    uint256 public minimumPrice;

    IERC721 public parentNFT;
    uint256 public tokenId;

    uint public revealTime;
    uint public winnerTime;

    enum AUCTION_STATE{
        CONTRACT_CREATION,
        RECIVEING_OFFERS,
        OFFER_REVEAL,
        CALCULATING_WINNER,
        AUCTION_ENDED
    }

    AUCTION_STATE public auction_state;

    constructor(bytes32 _minimumPriceHash, address _nftContract, uint256 _tokenId, uint _revealTime, uint _winnerTime) {
        auction_state = AUCTION_STATE.CONTRACT_CREATION;
        minimumPriceHash = _minimumPriceHash;
        parentNFT = IERC721(_nftContract);
        tokenId = _tokenId;
        revealTime = _revealTime;
        winnerTime = _winnerTime;
    }

    function transferAssetToContract() public onlyOwner{
        parentNFT.safeTransferFrom(_msgSender(), address(this), tokenId);
        auction_state = AUCTION_STATE.RECIVEING_OFFERS;
    }

    
    function makeOffer(bytes32 _hash) public virtual payable{
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS, 'Wrong auction state');
        require(_msgSender() != owner(), "Owner cant bid");
        require(msg.value > 0, "Need some ETH");
        require(accountToAmount[_msgSender()] == 0, "Cant bid twice"); // New participant.
        //event
        players.push(payable(_msgSender()));
        //event
        accountToAmount[_msgSender()] = msg.value;
        //event
        accountToHash[_msgSender()] = _hash;
    }

    function closeOffers() public{
        require(block.timestamp >= revealTime, 'Wait until set time');
        require(auction_state == AUCTION_STATE.RECIVEING_OFFERS, 'Wrong auction state');
        auction_state = AUCTION_STATE.OFFER_REVEAL;
    }

    function revealOffer(string memory _secret, uint256 _amount) public virtual{
    require(auction_state == AUCTION_STATE.OFFER_REVEAL, "Not right time");
    require(accountToAmount[_msgSender()] != 0, "You are not a participant"); // Participant
    require(accountToOffer[_msgSender()] == 0, "Can only reveal once"); // No retrys
    require(_amount <= accountToAmount[_msgSender()], "Offer invalidated"); 
    require(
        accountToHash[_msgSender()] == keccak256(
            abi.encodePacked(
                _secret,
                _amount
            )
        ), "Hashes do not match"
    ); // Hash match
    //event
    accountToOffer[_msgSender()] = _amount;
    }

    // ASolo 5 Seg en pruebas, cuando le hagas deploy hazlo con 30min minimo
    function closeReveals() public{
        require(block.timestamp >= winnerTime+5, 'Wait until set time'); //5s despues que vence tiempo de owner
        require(_msgSender() != owner(), "Owner must use winnerCalculation()");
        require(auction_state == AUCTION_STATE.OFFER_REVEAL, 'wrong auction state');
        auction_state = AUCTION_STATE.CALCULATING_WINNER;
        _closeReveals();
    }

    // Cambiale el nombre y pega el close reveals a final del metodo. Te mamas 
    function winnerCalculation(string memory _secret, uint256 _amount) public onlyOwner {
        require(auction_state == AUCTION_STATE.OFFER_REVEAL, 'Wrong auction state');
        require(block.timestamp >= winnerTime, 'Wait until set time');
        // Que el reveal al menos sea de 1 min ??? pon require si acaso
        require(
            minimumPriceHash == keccak256(
                abi.encodePacked(
                    _secret,
                    _amount
                )
            ), "Hashes do not match"
        );
        minimumPrice = _amount;
        auction_state = AUCTION_STATE.CALCULATING_WINNER;
        _closeReveals();
    }

    function _closeReveals() internal{ //internal
    // Verifia que el precio minimo este puesto. 
    uint256 indexOfWinner;
    uint256 loopAmount;
    uint256 i;
    if(players.length > 0){
        for(i = 0; i < players.length; i++){
            if(accountToOffer[players[i]] > loopAmount){
                indexOfWinner = i;
                loopAmount = accountToOffer[players[i]];
            }
        }
        if(loopAmount >= minimumPrice){
            winner = players[indexOfWinner];
            amount = accountToOffer[winner];
            // Quito lo ofrecido al que gana
            accountToAmount[winner] = accountToAmount[winner] - accountToOffer[winner];
        } 
    }
    auction_state = AUCTION_STATE.AUCTION_ENDED;
    }

    function ownerGetsPayed() public onlyOwner{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        if(amount > 0){
            uint256 toPay = amount;
            amount = 0; //No reentrancy
            payable(owner()).transfer(toPay);
        }else{
            // Nadie gana entonces regresa NFT al que crea subasta.
            parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
        }
    }

    function reimburseParticipant() public{
        // Tenga saldo positivo
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        uint256 reimbursement = accountToAmount[_msgSender()];
        require(reimbursement > 0);
        accountToAmount[_msgSender()] = 0; // no reent
        payable(_msgSender()).transfer(reimbursement);
    }

    function winnerRetrivesToken() public{
        require(auction_state == AUCTION_STATE.AUCTION_ENDED);
        require(_msgSender() == winner);
        parentNFT.safeTransferFrom(address(this), _msgSender(), tokenId);
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) public virtual override returns (bytes4){
         return this.onERC721Received.selector;
    }
}