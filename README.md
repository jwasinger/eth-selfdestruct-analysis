This repository contains results of an analyisis of the use of selfdestruct on Ethereum since the London hard-fork.

Two main use-cases for selfdestruct after the London hard-fork are as a contract upgrade mechanism by enabling the redeployment of new contracts at the same address, and creation of "ephemeral" contracts which can be created, used and deleted within the same transaction.

Usage of contract redeployments in `analysis-results/london-to-present/creators-of-redeployed-addrs.csv` shows 33 contracts which have redeployed one or more contracts at the same address.  None of the creator addresses hold significant Ether/token balances.

A list of addresses where multiple contracts have been deployed is in `analysis-results/london-to-present/redeployed-addrs.csv`.  A list of contracts which make use of ephemeral contracts is in `analysis-results/london-to-present/creators-of-ephemeral-contracts.csv`.

## Instructions for reproducing the results (TODO)
