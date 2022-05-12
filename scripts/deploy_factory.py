from brownie import AuctionFactory, SealedBidAuction, Contract, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import  get_account, hashStrings, time_now
from scripts.manage_nft import deploy_and_create_nft, create_nft



def deploy_factory(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret"):
    account = get_account(index=0)
    factory = AuctionFactory.deploy({"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    return factory


def deploy_factory_and_create_acution(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret"):
    account = get_account(index=0)
    initialHash = hashStrings(secret, min_price)
    collectible, collectible_id = deploy_and_create_nft()
    factory = AuctionFactory.deploy({"from": account}, publish_source = config["networks"][network.show_active()].get("verify", False))
    tx = factory.createSealedBidAuctionContract(initialHash, collectible, collectible_id, {"from": account})
    tx.wait(1)
    auctoin_index = tx.return_value
    auction_address = factory.sealedBidAuctionArray(auctoin_index)
    #print(auction_address)
    auction = Contract.from_abi( SealedBidAuction._name, auction_address, SealedBidAuction.abi)
    #print(auction.parentNFT())
    return auction, initialHash

def deploy_auction_from_factory(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret", time1=None, time2=None):
    account = get_account()
    initialHash = hashStrings(secret, min_price)
    factory = AuctionFactory[-1]
    #collectible, collectible_id = create_nft()
    collectible, collectible_id = deploy_and_create_nft()
    if not time1:
        time1 = 0
        time2 = 0
    tx = factory.createSealedBidAuctionContract(initialHash, collectible, collectible_id, time1, time2, {"from": account})
    tx.wait(1)
    auctoin_index = tx.return_value
    auction_address = factory.sealedBidAuctionArray(auctoin_index)
    #print(auction_address)
    auction = Contract.from_abi( SealedBidAuction._name, auction_address, SealedBidAuction.abi)
    #print(auction.parentNFT())
    #print(auction.tokenId())
    return auction, initialHash


def main():
    deploy_factory()
    #deploy_factory_and_create_acution()
    deploy_auction_from_factory()