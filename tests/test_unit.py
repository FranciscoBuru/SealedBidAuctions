from brownie import SealedBidAuction, accounts, config, network, exceptions
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, hashStrings, time_now
from scripts.deploy_auction import deploy_auction
from scripts.manage_nft import last_nft
import pytest
import time

MIN_PRICE = Web3.toWei(0.1, 'ether')
SECRET = "thisIsASecret"

def test_deploy():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    #Act
    collectible, collectible_id = last_nft()
    #Assert
    assert(auction.auction_state() == 1)
    assert(collectible.ownerOf(collectible_id) == auction)
    assert(str(auction.minimumPriceHash()) == hash.hex())
    assert(auction.owner() == get_account())

def test_owner_cant_participate():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    price = Web3.toWei(0.15, 'ether')
    secret = 'Secret1'
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    with pytest.raises(exceptions.VirtualMachineError):
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})


def test_min_amount_transfer():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    price = Web3.toWei(0, 'ether')
    secret = 'Secret1'
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    with pytest.raises(exceptions.VirtualMachineError):    
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})

def test_make_offer():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    price = Web3.toWei(0.16, 'ether')
    secret = 'Secret1'
    tx = auction.makeOffer(hashStrings(secret, price), {'from': account, 'value': price})
    tx.wait(1)
    assert(auction.accountToAmount(account) == price)
    assert(str(auction.accountToHash(account)) == hashStrings(secret, price).hex())
    assert(auction.players(0) == account)



def test_no_double_bids():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    price = Web3.toWei(0.15, 'ether')
    secret = 'Secret1'
    auction, hash = deploy_auction(MIN_PRICE, SECRET)
    tx = auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})
    tx.wait(1)
    price = Web3.toWei(0.13, 'ether')
    secret = 'Secret2'
    with pytest.raises(exceptions.VirtualMachineError):
        auction.makeOffer(hashStrings(secret, price), {"from": account, "value": price})


def test_close_bids_by_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    auction, hash = deploy_auction()
    tx = auction.closeOffers({'from':account})
    tx.wait(1)
    assert(auction.auction_state() == 2)

# El de abajo ya no tiene sentido porque el close depende del 
# timestamp ahora. 
'''def test_close_bids_by_not_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeOffers({'from':account})
        tx.wait(1)'''

def test_skip_reveal():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    auction, hash = deploy_auction()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':account})
        tx.wait(1)

def test_reveal_offer_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.toWei(0.16, 'ether')
    secret = 'Secret1'
    tx = auction.makeOffer(hashStrings(secret, price), {'from': account, 'value': price})
    tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(bytes(secret,'utf-8'), price, {'from':account})
        tx.wait(1)

def test_reveal_offer_not_participant():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    tx = auction.closeOffers({'from':get_account()})
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(bytes("secret",'utf-8'), Web3.toWei(0.16, 'ether'), {'from':account})
        tx.wait(1)

def test_encoding_matches():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.toWei(0.16, 'ether')
    secret = "Secret1"
    tx = auction.makeOffer(hashStrings(secret, price), {'from': account, 'value': price})
    tx.wait(1)
    print(auction.accountToHash(account))
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secret, price, {'from':account})
    tx.wait(1)
    assert(auction.accountToOffer(account) == price)
    


def test_cant_reveal_twice():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account(index=1)
    auction, hash = deploy_auction()
    price = Web3.toWei(0.16, 'ether')
    secret = 'Secret1'
    tx = auction.makeOffer(hashStrings(secret, price), {'from': account, 'value': price})
    tx.wait(1)
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secret, price, {'from':account})
    tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.revealOffer(secret, price, {'from':account})
        tx.wait(1)

def test_no_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.01, 'ether'),Web3.toWei(0.04, 'ether'),Web3.toWei(0.05, 'ether')]
    tx = auction.makeOffer(hashStrings(secrets[0], prices[0]), {'from': accounts[0], 'value': prices[0]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[1], prices[1]), {'from': accounts[1], 'value': prices[1]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[2], prices[2]), {'from': accounts[2], 'value': prices[2]})
    tx.wait(1)
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {'from':accounts[0]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {'from':accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {'from':accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':get_account()})
    tx.wait(1)
    #tx = auction.closeReveals({'from':get_account()})
    #tx.wait(1)
    assert(auction.winner() == "0x0000000000000000000000000000000000000000")
    assert(auction.amount() == 0)
    assert(auction.auction_state() == 4)
    return auction, accounts, prices

def test_give_token_back():
    auction, accounts, prices = test_no_winner()
    collectible, collectible_id = last_nft()
    assert(collectible.ownerOf(collectible_id) == auction)
    tx = auction.ownerGetsPayed({"from": get_account()})
    tx.wait(1)
    assert(collectible.ownerOf(collectible_id) == get_account())


def test_chooses_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.16, 'ether'),Web3.toWei(0.50, 'ether'),Web3.toWei(0.21, 'ether')]
    tx = auction.makeOffer(hashStrings(secrets[0], prices[0]), {'from': accounts[0], 'value': prices[0]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[1], prices[1]), {'from': accounts[1], 'value': prices[1]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[2], prices[2]), {'from': accounts[2], 'value': prices[2]})
    tx.wait(1)
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {'from':accounts[0]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {'from':accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {'from':accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':get_account()})
    tx.wait(1)
    #tx = auction.closeReveals({'from':get_account()})
    #tx.wait(1)
    assert(auction.winner() == accounts[1])
    assert(auction.amount() == prices[1])
    assert(auction.auction_state() == 4)
    return auction, accounts, prices

def test_participant_no_reveal():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2), get_account(index=3)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2", "S3"]
    prices = [Web3.toWei(0.16, 'ether'),Web3.toWei(0.50, 'ether'),Web3.toWei(0.21, 'ether')]
    tx = auction.makeOffer(hashStrings(secrets[0], prices[0]), {'from': accounts[0], 'value': prices[0]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[1], prices[1]), {'from': accounts[1], 'value': prices[1]})
    tx.wait(1)
    tx = auction.makeOffer(hashStrings(secrets[2], prices[2]), {'from': accounts[2], 'value': prices[2]})
    tx.wait(1)
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[1], prices[1], {'from':accounts[1]})
    tx.wait(1)
    tx = auction.revealOffer(secrets[2], prices[2], {'from':accounts[2]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':get_account()})
    tx.wait(1)
    #tx = auction.closeReveals({'from':get_account()})
    #tx.wait(1)
    assert(auction.winner() == accounts[1])
    assert(auction.amount() == prices[1])
    assert(auction.auction_state() == 4)
    return auction, accounts, prices

def test_auctioneer_gets_payed():
    account = get_account()
    auction, accounts, prices = test_chooses_winner_correctly()
    auction_initial_balance = auction.balance()
    account_initial_balance = account.balance()
    amount_sold_for = auction.amount()
    tx = auction.ownerGetsPayed({"from": account})
    tx.wait(1)
    assert(account_initial_balance + amount_sold_for == account.balance())
    assert(auction.balance() == auction_initial_balance - amount_sold_for )
    return auction, accounts, prices

def test_auctioneer_gets_payed_no_reveal():
    account = get_account()
    auction, accounts, prices = test_participant_no_reveal()
    auction_initial_balance = auction.balance()
    account_initial_balance = account.balance()
    amount_sold_for = auction.amount()
    tx = auction.ownerGetsPayed({"from": account})
    tx.wait(1)
    assert(account_initial_balance + amount_sold_for == account.balance())
    assert(auction.balance() == auction_initial_balance - amount_sold_for )
    return auction, accounts, prices

def test_reimbursements_no_reveal():
    auction, accounts, prices = test_auctioneer_gets_payed_no_reveal()
    auction_initial_balance = auction.balance()
    accounts_initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    tx = auction.reimburseParticipant({"from": accounts[2]})
    tx.wait(1)
    assert(accounts_initial_balances[0] + prices[0] == accounts[0].balance())
    assert(accounts_initial_balances[2] + prices[2] == accounts[2].balance())
    assert(auction_initial_balance - prices[0] - prices[2] == auction.balance())
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({'from':accounts[1]})
        tx.wait(1)
    return auction, accounts

def test_reimbursements():
    auction, accounts, prices = test_auctioneer_gets_payed()
    auction_initial_balance = auction.balance()
    accounts_initial_balances = [accounts[0].balance(), accounts[1].balance(), accounts[2].balance()]
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    tx = auction.reimburseParticipant({"from": accounts[2]})
    tx.wait(1)
    assert(accounts_initial_balances[0] + prices[0] == accounts[0].balance())
    assert(accounts_initial_balances[2] + prices[2] == accounts[2].balance())
    assert(auction_initial_balance - prices[0] - prices[2] == auction.balance())
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({'from':accounts[1]})
        tx.wait(1)
    return auction, accounts

def test_double_reinbursements():
    auction, accounts = test_reimbursements()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[0]})
        tx.wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({"from": accounts[2]})
        tx.wait(1)


def test_winner_gives_more_than_offered():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    accounts = [get_account(index=1), get_account(index=2)]
    auction, hash = deploy_auction()
    secrets = ["S1", "S2"]
    prices = [Web3.toWei(0.1, 'ether'), Web3.toWei(0.1, 'ether')]
    tx = auction.makeOffer(hashStrings(secrets[0], prices[0]), {'from': accounts[0], 'value':  Web3.toWei(0.5, 'ether')})
    tx.wait(1)
    tx = auction.closeOffers({'from':get_account()})
    tx.wait(1)
    tx = auction.revealOffer(secrets[0], prices[0], {'from':accounts[0]})
    tx.wait(1)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {'from':get_account()})
    tx.wait(1)
    #tx = auction.closeReveals({'from':get_account()})
    #tx.wait(1)
    contract_balance = auction.balance()
    participant_balance = accounts[0].balance()
    assert(auction.accountToAmount(accounts[0]) == Web3.toWei(0.4, 'ether'))
    tx = auction.reimburseParticipant({"from": accounts[0]})
    tx.wait(1)
    assert(contract_balance - auction.accountToOffer(accounts[0]) == Web3.toWei(0.4, 'ether'))
    assert(participant_balance + Web3.toWei(0.4, 'ether') == accounts[0].balance())
    assert(auction.accountToAmount(accounts[0]) == 0)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.reimburseParticipant({'from':accounts[0]})
        tx.wait(1)

def test_winner_retrives_token():
    auction, accounts, prices = test_chooses_winner_correctly()
    collectible, collectible_id = last_nft()
    assert(collectible.ownerOf(collectible_id) == auction)
    tx = auction.winnerRetrivesToken({"from": accounts[1]})
    tx.wait(1)
    assert(collectible.ownerOf(collectible_id) == accounts[1])

def test_non_winner_retrives_token():
    auction, accounts, prices = test_chooses_winner_correctly()
    collectible, collectible_id = last_nft()
    assert(collectible.ownerOf(collectible_id) == auction)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerRetrivesToken({"from": accounts[0]})
        tx.wait(1)
    assert(collectible.ownerOf(collectible_id) == auction)


## Tests con tiempos en cuenta

#Revisa que variables del contrato sean correctas despues del deploy
def test_right_times_deploy():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    time1 = time_now()+5
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    #Act
    collectible, collectible_id = last_nft()
    #Assert
    assert(auction.auction_state() == 1)
    assert(collectible.ownerOf(collectible_id) == auction)
    assert(str(auction.minimumPriceHash()) == hash.hex())
    assert(auction.owner() == get_account())
    assert(auction.revealTime() == time1)
    assert(auction.winnerTime() == time2)

def test_cant_close_offers_on_wrong_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    account = get_account()
    time1 = time_now()+50
    time2 = time1 + 100
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    #Act
    collectible, collectible_id = last_nft()
    #Assert
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeOffers({"from": account})
        tx.wait(1)
    return account, auction

def test_cant_close_offers_on_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    account2 = get_account(index=1)
    time1 = time_now()+50
    time2 = time1 + 100
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    #Assert
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeOffers({"from": account2})
        tx.wait(1)
    return account2, auction

def test_close_offers_right_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    account = get_account(index=2)
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    #Act
    time.sleep(5)
    #Assert
    tx = auction.closeOffers({"from": account})
    tx.wait(1)
    assert(auction.auction_state() == 2)
    return account, auction

def test_close_offers_right_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    #Arrange
    account = get_account()
    time1 = time_now()
    time2 = time1 + 10
    auction, hash = deploy_auction(MIN_PRICE, SECRET, time1, time2)
    #Act
    time.sleep(5)
    #Assert
    tx = auction.closeOffers({"from": account})
    tx.wait(1)
    assert(auction.auction_state() == 2)
    return account, auction

def test_close_reveals_wrong_time():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeReveals({"from": account})
        tx.wait(1)

def test_close_reveals_wrong_time_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)

def test_close_reveals_wrong_method():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(5)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)

def test_close_reveals_wrong_method_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    #Act
    time.sleep(5)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeReveals({"from": account})
        tx.wait(1)

#Me salvo para poner if dentro de _closeReveals
#Diff
def test_close_reveals_right_time_and_method():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(10)
    tx = auction.closeReveals({"from": account})
    tx.wait(1)
    assert(auction.auction_state() == 4)

def test_close_reveals_right_time_and_method_with_diffrence():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time()
    time.sleep(1)
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.closeReveals({"from": account})
        tx.wait(1)


def test_close_reveals_right_time_and_method_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    time.sleep(5)
    tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
    tx.wait(1)
    assert(auction.auction_state() == 4)

def test_close_reveals_right_time_and_method_with_diffrence_owner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account, auction = test_close_offers_right_time_owner()
    with pytest.raises(exceptions.VirtualMachineError):
        tx = auction.winnerCalculation(SECRET, MIN_PRICE, {"from": account})
        tx.wait(1)




