# Analysis of selfdestruct usage on Ethereum after the London hard fork
https://github.com/ethereum/EIPs/pull/4758 is a proposal which changes the behavior of the EVM `SELFDESTRUCT` opcode and renames it to `SENDALL`.  `SENDALL` removes the contract destruction aspect of `SELFDESTRUCT` while retaining the behavior which instantly transfers the balance of the executing contract to a target recipient.

There are two main use-cases for selfdestruct after the London hard fork:

* an address calculated by `create2` can have contracts deployed, selfdestructed and redeployed (with new bytecode).  This serves as a way to update a contract.
* contracts can be created, used, and selfdestructed within the same transaction.

Both of these use-cases would become non-viable with the replacement of `SELFDESTRUCT` with `SENDALL`.

Because `SENDALL` retains the eth transfer behavior of `SELFDESTRUCT`, any selfdestructable contracts which are currently deployed should not be at risk of getting their Ether locked/lost if the change goes through.  However, creators of selfdestructable contracts could be broken: a created contract which was previously selfdestructable, would no longer be removed after executing `SENDALL`.  The next attempted creation of a contract at that address would fail with the creation endowment remaining in the creator contract (potentially being locked depending on how that contract is written).

### Results

Analysis shows that 33 creator contracts have redeployed one or more child contract at the same address (`analysis-results/london-to-present/creators-of-redeployed-addrs.csv`).  None of these contracts contain significant ether/token balances.  There are 38 contracts which have created multiple ephemeral contracts at the same address (`analysis-results/london-to-present/ephemeral-creators-which-reuse-addrs.csv`).  Two of these addresses contain significant Ether balances and together contain $55,000 USD worth of Ether (as of March 23rd, 2022).

## Instructions for reproducing the results (TODO)
