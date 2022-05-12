from brownie import SealedBidAuction, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import  get_account, hashStrings, time_now
from scripts.manage_nft import deploy_and_create_nft, create_nft



def deploy_auction(min_price = Web3.toWei(0.1, 'ether') , secret = "thisIsASecret", time = None, time2 = None):
    account = get_account(index=0)
    initialHash = hashStrings(secret, min_price)
    collectible, collectible_id = deploy_and_create_nft()
    if not time:
        time = 0
        time2 = 0 
    auction = SealedBidAuction.deploy(
        initialHash, 
        collectible, 
        collectible_id, 
        time, 
        time2, {"from": account}, 
        publish_source = config["networks"][network.show_active()].get("verify", False))
    tx = collectible.approve(auction, collectible_id, {"from": account})
    print(tx.timestamp)
    tx.wait(1)
    tx = auction.transferAssetToContract({"from": account})
    tx.wait(1)
    return auction, initialHash


def main():
    deploy_auction()
