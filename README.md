# Analysis of Selfdestruct Usage on Ethereum after the London Hard Fork
https://github.com/ethereum/EIPs/pull/4758 is a proposal which changes the behavior of the EVM `SELFDESTRUCT` opcode and renames it to `SENDALL`.  `SENDALL` removes the contract destruction aspect of `SELFDESTRUCT` while retaining the behavior which instantly transfers the balance of the executing contract to a target recipient.

There are two main use-cases for selfdestruct after the London hard fork:
* an address calculated by `create2` can have contracts deployed, selfdestructed and redeployed (with new bytecode).  This serves as a way to update a contract.
* contracts can be created, used, and selfdestructed within the same transaction.

In both cases, it can result that an address will be destroyed and created one or more times.  This is referred to as a `re-inited` address.

## Results

From Genesis to block 12,799,316, there were 11304 contracts which redeployed, 69102 addresses which were re-inited one or more times.

Since London (block 12,965,000), 34 contracts redeployed child contracts and 238 addresses were re-inited.  The 12 re-inited addresses with nonzero Ether balances have 4430 Ether together.  Two of the creators of addresses that selfdestructed have Ether/tokens with a total value of ~$55000 USD (as of March 25th, 2022).  None of these have contract source code on Etherscan.
It's difficult to determine with certainty, every single address that would be at risk of losing funds with the change of `SELFDESTRUCT` to `SENDALL`.  None of the contracts which are creators of re-inited contracts, or any re-inited contracts have their source verified on Etherscan.  However, looking at the balances of potentially-affected addresses reveals that most of the Ether holdings are concentrated in a few addresses.

Here are twenty addresses with the highest Ether balances:

| Address | Ether Balance |
| --------------------------- | --- | 
|0x000000000000006f6502b7f2bbac8c30a3f67e9a| 3324.420061694295|
|0x66be1bc6c6af47900bbd4f3711801be6c2c6cb32| 1901.0612243907497|
|0x0000000000007f150bd6f54c40a34d7c3d5e9f56| 1052.0346555690187|
|0x8bc110db7029197c3621bea8092ab1996d5dd7be| 522.381685684114|
|0x30b84dc1a46c58e0bcfe6aa9f74042dff159277a| 140.56124777053802|
|0x36049d479a97cde1fc6e2a5d2cae30b666ebf92b| 98.89128076172763|
|0x3dca07e16b2becd3eb76a9f9ce240b525451f887| 84.90239709803015|
|0x9998569436887938287223231949815647232697| 84.00239483914334|
|0xbe4a176b0d18f1e158cc1a833383212f68327b51| 58.12295457143919|
|0x000000000035b5e5ad9019092c665357240f594e| 33.67848284726566|
|0x983b45f89198b3356e81bc09a0fa1933bbea1d76| 28.036818265914945|
|0x5b1b0349b3a668c75cc868801a39430684e3f36a| 19.98447425583028|
|0x206548d60d891aefc16cf899af75e3527148941a| 13.571287045047718|
|0x0000000099cb7fc48a935bceb9f05bbae54e8987| 11.07584061230294|
|0xd412054cca18a61278ced6f674a526a6940ebd84| 7.271706101417892|
|0xafe87013dc96ede1e116a288d80fcaa0effe5fe5| 5.5812284324692545|
|0xa95baf5ef81707aa56625a9302a7f7d3aaf12ef4| 5.509614527057623|
|0x2222222229b89c7844f19ef503c4dc503be47f84| 4.784371587066971|
|0x8e2dc6d9318eedda52335afe8ef4ff1cf3883cae| 4.348183572554626|
|0x6b2b69c6e5490be701abfbfa440174f808c1a33b| 4.045736144113548|

It seems likely that every potentially-affected address with large Ether/ERC20 holdings will need to be analyzed to determine if it could be broken.

Some next steps to proceed with the analysis are:
* Identifying contracts from the list of potentially-affected which hold large/valuable ERC20 balances.
* Identifying currently-existing selfdestructable contracts which were deployed via `create2` and determining of these and their creators, which have large ERC20/Ether holdings.

Once there is a full list of potentially-affected contracts, per-contract analysis can be done for contracts with large holdings.

## Running the Analysis

The first step is to retrieve the raw dataset of contract creation / selfdestruct internal transaction traces from the BigQuery Ethereum dataset with the following query:

```
select block_hash, transaction_hash,  trace_id, block_number, transaction_index, from_address, to_address, trace_type, call_type, status, value from `bigquery-public-data.crypto_ethereum.traces` 
    where (trace_type='suicide' or trace_type = 'create')
    order by block_number asc, transaction_index asc
```

The data is rather large and must be exported as multiple csv files to a GCS bucket.  When exporting from BigQuery to GCS, choose `data-*.csv` as the naming format for the exported files.  Download these csvs to a folder `data-traces` placed in the top-level directory of this repo.  Execute the script `rename-files.py` to rename the downloaded files so that their data is ordered properly (i.e. the layout of the data in `data-0001.csv`, `data-0002.csv`, ... is chronological.  when the files are downloaded from the storage bucket, the numerical prefix assigned to a given csv is somewhat random).

Execute the analysis by running `analyze.py`.

The analysis script produces several results:
* `creators-of-redeployed-addrs.csv` - list of any contract that created an child contract which was redeployed.
* `creators-of-ephemeral-contracts.csv` - list of accounts which created ephemeral contracts.
* `redeployed-addrs.csv` - a list of addresses which had re-inits.

To get a list of Ether balances for all accounts in these three csvs, execute `query_balances_for_creators_and_reinited_addrs.py`.
