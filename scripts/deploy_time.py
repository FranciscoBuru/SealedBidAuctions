from brownie import TimeOracle, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import  get_account, hashStrings, time_now, TESTNETS
from scripts.manage_nft import deploy_and_create_nft, create_nft

# Rinkeby
price_feeds = [
    '0x8A753747A1Fa494EC906cE90E9f37563A8AF630e',
    '0xCe3f7378aE409e1CE0dD6fFA70ab683326b73f04',
    '0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e',
    '0x13E99C19833F557672B67C70508061A2E1e54162'
]

def deploy_time():
    if network.show_active() not in TESTNETS:
        pass
    else:
        account = get_account()
        time_oracle = TimeOracle.deploy({"from": account}, 
            publish_source = config["networks"][network.show_active()].get("verify", False))
        return time_oracle

def get_last_deployed_time():
    if len(TimeOracle) > 0:
        return TimeOracle[-1]


def deploy_and_add_addresses():
    time_contract = deploy_time()
    account = get_account()
    # Agrega Feeds
    for feed in price_feeds:
        time_contract.addPriceFeed(feed, {"from": account})
    return time_contract

def delete_feed():
    account = get_account()
    time_contract = get_last_deployed_time()
    time_contract.deletePriceFeed(price_feeds[2], {"from": account})

def print_data(time_contract):
    for i in range(time_contract.getLength()):
        print(time_contract.timeFeed(i))
    print(time_contract.getLatestTime())

def main():
    #time_contract = get_last_deployed_time()
    time_contract = deploy_and_add_addresses()
    print_data(time_contract)
    delete_feed()
    print_data(time_contract)
    add_one_feed()
    print_data(time_contract)

def add_one_feed():
    account = get_account()
    time_contract = get_last_deployed_time()
    time_contract.addPriceFeed(price_feeds[2], {"from": account})





