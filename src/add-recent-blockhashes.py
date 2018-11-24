import time
import rlp
from web3 import Web3, WebsocketProvider
from hexbytes import HexBytes
from websockets import exceptions as websockets_errors

ZERO = '0x0000000000000000000000000000000000000000000000000000000000000000'
GWEI = 1000000000
WS1 = WebsocketProvider('ws://128.235.40.191:8546')
WS2 = WebsocketProvider('ws://128.235.40.169:8546')


def init():
    abi = '[{"constant":false,"inputs":[{"name":"n","type":"uint256"},{"name":"child_header","type":"bytes"}],"name":"add_old","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"hashes","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"n","type":"uint256"}],"name":"get_blockhash","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"n","type":"uint256"}],"name":"add_recent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"msg","type":"string"}],"name":"Error","type":"event"}]'
    bin = '0x608060405234801561001057600080fd5b50610446806100206000396000f300608060405260043610610062576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063440397e114610067578063501895ae146100da578063baa2ff0114610123578063c1f979ab1461016c575b600080fd5b34801561007357600080fd5b506100d860048036038101908080359060200190929190803590602001908201803590602001908080601f0160208091040260200160405190810160405280939291908181526020018383808284378201915050505050509192919290505050610199565b005b3480156100e657600080fd5b5061010560048036038101908080359060200190929190505050610343565b60405180826000191660001916815260200191505060405180910390f35b34801561012f57600080fd5b5061014e6004803603810190808035906020019092919050505061035b565b60405180826000191660001916815260200191505060405180910390f35b34801561017857600080fd5b5061019760048036038101908080359060200190929190505050610377565b005b60006060600080600080600188018152602001908152602001600020549350846040518082805190602001908083835b6020831015156101ee57805182526020820191506020810190506020830392506101c9565b6001836020036101000a038019825116818451168082178552505050505050905001915050604051809103902060001916846000191614151561022d57fe5b60206040519080825280601f01601f1916602001820160405280156102615781602001602082028038833980820191505090505b509250600091505b602082101561031957846004830181518110151561028357fe5b9060200101517f010000000000000000000000000000000000000000000000000000000000000090047f01000000000000000000000000000000000000000000000000000000000000000283838151811015156102dc57fe5b9060200101907effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916908160001a9053508180600101925050610269565b60208301519050806000808881526020019081526020016000208160001916905550505050505050565b60006020528060005260406000206000915090505481565b6000806000838152602001908152602001600020549050919050565b6000814090506000600102816000191614156103fa577f08c379a0afcc32b1a39302f7cb8073359698411ab5fd6e3edb2c02c0b5fba8aa60405180806020018281038252600f8152602001807f626c6f636b68617368206661696c73000000000000000000000000000000000081525060200191505060405180910390a1610416565b8060008084815260200190815260200160002081600019169055505b50505600a165627a7a723058206f60b72f308387bc08492caa7ab91da704d36290d75d1e66c14786facb3245960029'
    addr = Web3.toChecksumAddress('0xb11ea8d6bab4c557a781785425a2c5654f882663')
    w3 = Web3(WS1)
    if w3.isConnected():
        print("Connected to:" + w3.version.node)
        if w3.eth.syncing:
            print("Warning: ws node is syncing")
        print('Enter the password:')
        pwd = input()
        while not w3.personal.unlockAccount(w3.personal.listAccounts[0], pwd):
            print('Enter the correct password:')
            pwd = input()
        w3.eth.defaultAccount = w3.eth.accounts[0]
        print('Accounts unlocked!')
        c = w3.eth.contract(abi=abi, bytecode=bin, address=addr)
        return w3, c, pwd
    else:
        print("Not connected to ws node")
        exit(255)


def block_to_rlp_encoded_header(block):
    h = [
        HexBytes(block.parentHash),
        HexBytes(block.sha3Uncles),
        HexBytes(block.miner),
        HexBytes(block.stateRoot),
        HexBytes(block.transactionsRoot),
        HexBytes(block.receiptsRoot),
        HexBytes(block.logsBloom),
        HexBytes(web3.toHex(block.difficulty)),
        HexBytes(web3.toHex(block.number)),
        HexBytes(web3.toHex(block.gasLimit)),
        HexBytes(web3.toHex(block.gasUsed)),
        HexBytes(web3.toHex(block.timestamp)),
        HexBytes(block.extraData),
        HexBytes(block.mixHash),
        HexBytes(block.nonce)
    ]
    print(h)
    return rlp.encode(h)


def insert_recent_blockhash(block_num):
    if web3.toHex(contract.functions.get_blockhash(block_num).call()) == ZERO:
        print('Inserting hash of block at %d ...' % block_num)
        tx_hash = contract.functions.add_recent(block_num).transact()
        print(web3.toHex(tx_hash))
        time.sleep(1)

if __name__ == '__main__':
    web3, contract, password = init()
    while True:
        try:
            latest_block = web3.eth.getBlock('latest').number
            print('Latest block: %d' % latest_block)
            for i in range(99, -1, -1):
                insert_recent_blockhash(latest_block - i)
            web3.personal.unlockAccount(web3.eth.accounts[1], password)
            web3.eth.defaultAccount = web3.eth.accounts[1]
        except ValueError:
            continue
        except websockets_errors.ConnectionClosed as e:
            print(e)
            exit(255)
        finally:
            time.sleep(60*2)

    # stored_block = 0
    # while True:
    #     latest_block = web3.eth.getBlock('latest').number
    #     print('latest_block: %d' % latest_block)
    #     if latest_block > stored_block:
    #         if latest_block > stored_block + 250:
    #             stored_block = latest_block - 250
    #             while stored_block < latest_block:
    #                 print('stored_block: %d' % stored_block)
    #                 stored_block = insert_recent_blockhash(stored_block)
    #         else:
    #             while stored_block < latest_block:
    #                 print('stored_block: %d' % stored_block)
    #                 stored_block = insert_recent_blockhash(stored_block)
    #     time.sleep(30)
    #     web3.personal.unlockAccount(web3.eth.accounts[0], PWD)
    #     web3.eth.defaultAccount = web3.eth.accounts[0]

    # Solidity source code
    # '''
    # pragma solidity ^0.4.25;
    #
    # contract Blockhashes {
    #
    #     mapping(uint => bytes32) public hashes;
    #     event Error(string msg);
    #
    #     function add_recent (uint n) public {
    #         bytes32 h = blockhash(n);
    #         if (h == 0) {
    #             emit Error("blockhash fails");
    #         } else {
    #             hashes[n] = h;
    #         }
    #     }
    #
    #     function add_old (uint n, bytes memory child_header) public {
    #         bytes32 child_hash = hashes[n+1];
    #         assert(child_hash == keccak256(child_header));
    #         bytes memory parent_hash = new bytes(32);
    #         for(uint i=0; i< 32; i++){
    #             parent_hash[i] = child_header[i+4];
    #         }
    #         bytes32 h;
    #         assembly {
    #             h := mload(add(parent_hash, 32))
    #         }
    #         hashes[n] = h;
    #     }
    #
    #     function get_blockhash (uint n) public constant returns (bytes32) {
    #         return hashes[n];
    #     }
    #
    # }
    # '''

