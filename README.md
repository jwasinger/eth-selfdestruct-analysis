# Analysis of selfdestruct usage on Ethereum after the London hard fork
https://github.com/ethereum/EIPs/pull/4758 is a proposal which changes the behavior of the EVM `SELFDESTRUCT` opcode and renames it to `SENDALL`.  `SENDALL` removes the contract destruction aspect of `SELFDESTRUCT` while retaining the behavior which instantly transfers the balance of the executing contract to a target recipient.

There are two main use-cases for selfdestruct after the London hard fork:

* an address calculated by `create2` can have contracts deployed, selfdestructed and redeployed (with new bytecode).  This serves as a way to update a contract.
* contracts can be created, used, and selfdestructed within the same transaction.

Both of these use-cases would become non-viable with the replacement of `SELFDESTRUCT` with `SENDALL`.


From Genesis to block 12799316, there were 11304 contracts which redeployed child contracts, 69102 addresses which had one or more re-inits.

Since London, 34 contracts redeployed child contracts and 238 addresses have re-inits.  The 12 re-inited addresses with nonzero balances have 4430 Ether together.  Two of the creators of addresses that selfdestructed have Ether/tokens with a total value of ~$55000 USD (as of March 25th, 2022).  None of these have contract source code on Etherscan.

It's difficult to determine every single address that would be at risk of lost funds because many selfdestructable contracts and creators of these contracts are not verified on Etherscan.  However, ether/ERC20 balances reveal high concentration of affected funds in whale accounts:

| Address with re-init(s) | Ether Balance |
---------------------------
|0x0000000099cb7fc48a935bceb9f05bbae54e8987| 12.15342213200995|
|0x000000000000006f6502b7f2bbac8c30a3f67e9a| 3324.4140871710733|
|0x00000000032962b51589768828ad878876299e14| 3.051639286062525|
|0x000000e1fddf4fe15db5f23ae3ee83c6a11e8dd1| 0.01|
|0x000000000035b5e5ad9019092c665357240f594e| 35.824890136908934|
|0xf2d47e78dea8e0f96902c85902323d2a2012b0c0| 3.3781819040953978|
|0xa1006d0051a35b0000f961a8000000009ea8d2db| 4.120442258e-09|
|0x00000000003503bad07dc2c8027052c5880d46cc| 0.05058310914906227|
|0x01ff6318440f7d5553a82294d78262d5f5084eff| 2.63155283e-09|
|0x499dd900f800fd0a2ed300006000a57f00fa009b| 0.18037058919772106|
|0xb3fcd22ffd34d75c979d49e2e5fb3a3405644831| 0.3936493854356113|
|0x0000000000007f150bd6f54c40a34d7c3d5e9f56| 1050.7502029949273|

**TODO** include deployers in this chart, sort the chart descending by balance

**TODO** USD value of balances for important ERC20 tokens in potentially-affected accounts

## Instructions for reproducing the results (TODO)
