# Selfdestruct Analysis

chain tx analysis:
* gather all addresses which had contracts redeployed at them OR are contract accounts that deployed/redeployed a selfdestructable contract.
	* gather all contract addresses that were "progenitors" in the creation line for selfdestructable contracts.
* gather all contract addresses (and progenitors) which deployed ephemeral contracts (contracts that created/selfdestructed in the same transaction).

contract code analysis:
* find all contracts containing SELFDESTRUCT
* search all deployed contract code for references to redeployable/ephemeral addresses in push-data

---

and then with this list, manually look into the contracts which:
* have a non-trivial Ether balance
* get called most often
* have large aggregate gas usage over the course of the analysis period
