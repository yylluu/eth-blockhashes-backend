import rlp
from web3 import Web3, WebsocketProvider
from websockets import exceptions as websockets_errors
from ethereum import block
from ethereum.utils import (
    normalize_address, bytes_to_int
)

ZERO = '0x0000000000000000000000000000000000000000000000000000000000000000'


def init():
    abi = '[{"constant":false,"inputs":[{"name":"n","type":"uint256"},{"name":"child_header","type":"bytes"}],"name":"add_old","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"hashes","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"n","type":"uint256"}],"name":"get_blockhash","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"n","type":"uint256"}],"name":"add_recent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"msg","type":"string"}],"name":"Error","type":"event"}]'
    bin = '0x608060405234801561001057600080fd5b50610446806100206000396000f300608060405260043610610062576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063440397e114610067578063501895ae146100da578063baa2ff0114610123578063c1f979ab1461016c575b600080fd5b34801561007357600080fd5b506100d860048036038101908080359060200190929190803590602001908201803590602001908080601f0160208091040260200160405190810160405280939291908181526020018383808284378201915050505050509192919290505050610199565b005b3480156100e657600080fd5b5061010560048036038101908080359060200190929190505050610343565b60405180826000191660001916815260200191505060405180910390f35b34801561012f57600080fd5b5061014e6004803603810190808035906020019092919050505061035b565b60405180826000191660001916815260200191505060405180910390f35b34801561017857600080fd5b5061019760048036038101908080359060200190929190505050610377565b005b60006060600080600080600188018152602001908152602001600020549350846040518082805190602001908083835b6020831015156101ee57805182526020820191506020810190506020830392506101c9565b6001836020036101000a038019825116818451168082178552505050505050905001915050604051809103902060001916846000191614151561022d57fe5b60206040519080825280601f01601f1916602001820160405280156102615781602001602082028038833980820191505090505b509250600091505b602082101561031957846004830181518110151561028357fe5b9060200101517f010000000000000000000000000000000000000000000000000000000000000090047f01000000000000000000000000000000000000000000000000000000000000000283838151811015156102dc57fe5b9060200101907effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916908160001a9053508180600101925050610269565b60208301519050806000808881526020019081526020016000208160001916905550505050505050565b60006020528060005260406000206000915090505481565b6000806000838152602001908152602001600020549050919050565b6000814090506000600102816000191614156103fa577f08c379a0afcc32b1a39302f7cb8073359698411ab5fd6e3edb2c02c0b5fba8aa60405180806020018281038252600f8152602001807f626c6f636b68617368206661696c73000000000000000000000000000000000081525060200191505060405180910390a1610416565b8060008084815260200190815260200160002081600019169055505b50505600a165627a7a723058206f60b72f308387bc08492caa7ab91da704d36290d75d1e66c14786facb3245960029'
    addr = Web3.toChecksumAddress('0xb11ea8d6bab4c557a781785425a2c5654f882663')
    w3 = Web3(WebsocketProvider('ws://128.235.40.191:8546'))
    if w3.isConnected():
        print("Connected to:" + w3.version.node)
        if w3.eth.syncing:
            print("Warning: ws node is syncing")
        print('Enter the password:')
        pwd = input()
        for account in w3.personal.listAccounts:
            w3.personal.unlockAccount(account, pwd)
        w3.eth.defaultAccount = w3.eth.accounts[1]
        print('Accounts unlocked!')
        c = w3.eth.contract(abi=abi, bytecode=bin, address=addr)
        return w3, c, pwd
    else:
        print("Not connected to ws node")
        exit(255)


def block_to_rlp_encoded_header(block_attr_dict):
    #print(block_attr_dict)
    header = block.BlockHeader(
        bytes(block_attr_dict.parentHash),
        bytes(block_attr_dict.sha3Uncles),
        normalize_address(block_attr_dict.miner),
        bytes(block_attr_dict.stateRoot),
        bytes(block_attr_dict.transactionsRoot),
        bytes(block_attr_dict.receiptsRoot),
        bytes_to_int(bytes(block_attr_dict.logsBloom)),
        block_attr_dict.difficulty,
        block_attr_dict.number,
        block_attr_dict.gasLimit,
        block_attr_dict.gasUsed,
        block_attr_dict.timestamp,
        bytes(block_attr_dict.extraData),
        bytes(block_attr_dict.mixHash),
        bytes(block_attr_dict.nonce)
    )
    return rlp.encode(header)


def insert_old_blockhash(block):
    web3.personal.unlockAccount(web3.eth.accounts[1], pwd)
    web3.eth.defaultAccount = web3.eth.accounts[1]
    if web3.toHex(contract.functions.get_blockhash(block + 1).call()) != ZERO:
        child_header = web3.toHex(block_to_rlp_encoded_header(web3.eth.getBlock(block + 1)))
        print(child_header)
        print('Inserting hash of block at %d ...' % block)
        try:
            print(contract.functions.add_old(block, child_header).estimateGas())
            tx_hash = contract.functions.add_old(block, child_header).transact()
            print(web3.toHex(tx_hash))
            tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
            return web3.toHex(contract.functions.get_blockhash(block).call())
        except ValueError as e:
            print(e)
            print(web3.eth.getBlock(block + 1))
            return ZERO
    else:
        return ZERO


if __name__ == '__main__':
    web3, contract, pwd = init()
    latest_block = web3.eth.getBlock('latest').number

    for block_num in range(4476961 - 1, 4000000 - 1, -1):
        if web3.toHex(contract.functions.get_blockhash(block_num).call()) == ZERO:
            try:
                insert_old_blockhash(block_num)
            except ValueError:
                continue
            except websockets_errors.ConnectionClosed:
                exit(255)

    # for block in range(4477000, latest_block):
    #     if web3.toHex(contract.functions.get_blockhash(block).call()) == ZERO:
    #         insert_old_blockhash(block)

# Solidity source code
'''
pragma solidity ^0.4.25;

contract Blockhashes {
    
    mapping(uint => bytes32) public hashes;
    event Error(string msg);
    
    function add_recent (uint n) public {
        bytes32 h = blockhash(n);
        if (h == 0) {
            emit Error("blockhash fails");
        } else {
            hashes[n] = h;
        }
    }
    
    function add_old (uint n, bytes memory child_header) public {
        bytes32 child_hash = hashes[n+1];
        assert(child_hash == keccak256(child_header));
        bytes memory parent_hash = new bytes(32);
        for(uint i=0; i< 32; i++){
            parent_hash[i] = child_header[i+4];
        }
        bytes32 h;
        assembly {
            h := mload(add(parent_hash, 32))
        }
        hashes[n] = h;
    }
    
    function get_blockhash (uint n) public constant returns (bytes32) {
        return hashes[n];
    }

}
'''
