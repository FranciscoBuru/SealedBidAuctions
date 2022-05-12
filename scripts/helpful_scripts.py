from brownie import network, config, accounts, Contract, SealedBidAuction
from web3 import Web3
from Crypto.Hash import keccak
import math
import time

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganace-local', 'mainnet-fork']
TESTNETS = ['rinkeby']


def get_account(index = None, id = None, number=None):
    # accounts[0]
    # accounts.add("env")
    # account.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # id="freecodecamp-account"
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        if number:
            if number == 0:
                return accounts.add(config["wallets"][f"from_key"])
            else:
                return accounts.add(config["wallets"][f"from_key{number}"])
        else:
            return accounts.add(config["wallets"]["from_key"])
    else:
        return None

def hashStrings(s1, s2):
    ans = Web3.solidityKeccak(['bytes32','uint256'],[bytes(s1,'utf-8'), int(s2)])
    return ans


def time_now():
    return math.floor(time.time())

#price = Web3.toWei(0.16, 'ether')
#secret = 'Secret1'
#ans = hashStrings(secret,price)
#print(ans)
#print(Web3.toBytes(text=secret))
#print(price)
#ans = hashStrings(secret,price)
#ans = Web3.solidityKeccak(['bytes32','uint256'],[bytes('Secret1','utf-8'), 160000000000000000])
#print(ans.hex())
