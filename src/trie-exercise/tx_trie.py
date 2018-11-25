from ethereum import transactions
from ethereum.utils import (
    normalize_address, bytes_to_int
)
import rlp
from web3 import Web3, WebsocketProvider
import codecs
from ethereum.trie import Trie, BLANK_ROOT
from ethereum.db import DB
WS1 = WebsocketProvider('ws://128.235.40.191:8546')


def init():
    w3 = Web3(WS1)
    if w3.isConnected():
        print("Connected to:" + w3.version.node)
        if w3.eth.syncing:
            print("Warning: ws node is syncing")
        print('Enter the password:')
        while not w3.personal.unlockAccount(w3.personal.listAccounts[0], input()):
            print('Enter the correct password:')
        w3.eth.defaultAccount = w3.eth.accounts[0]
        print('Accounts unlocked!')
        return w3
    else:
        print("Not connected to ws node")
        exit(255)


def tx_to_rlp_encoded_tx(tx_attr_dict):
    tx = transactions.Transaction(
        tx_attr_dict.nonce,
        tx_attr_dict.gasPrice,
        tx_attr_dict.gas,
        normalize_address(tx_attr_dict.to),
        tx_attr_dict.value,
        codecs.decode(tx_attr_dict.input.replace("0x", ""), 'hex'),
        tx_attr_dict.v,
        bytes_to_int(tx_attr_dict.r),
        bytes_to_int(tx_attr_dict.s)
    )
    return rlp.encode(tx)


# Ropsten testnet block number 4498850 contains only one tx:
# 0xca2dc2bfadb212ddd080bad80cf58902e8a3596e90f1a022daa5e7e635008a67
# Its tx root is as follows:
# b1c1f0db6fc70fe23b85dc39b4d4eac898f186d61990131b981d1f8ed5c746c6


web3 = init()
transaction = web3.eth.getTransaction('0xca2dc2bfadb212ddd080bad80cf58902e8a3596e90f1a022daa5e7e635008a67')
print(transaction)
encoded_tx = tx_to_rlp_encoded_tx(transaction)
print(web3.toHex(encoded_tx))
print(web3.toHex(web3.sha3(encoded_tx)))

db = DB()
trie = Trie(db, BLANK_ROOT)
print('root hash', trie.root_hash)
print('root hash', codecs.encode(trie.root_hash, 'hex'))
trie.update(rlp.encode(0), (encoded_tx))
print('root hash', trie.root_hash)
print('root hash', codecs.encode(trie.root_hash, 'hex'))