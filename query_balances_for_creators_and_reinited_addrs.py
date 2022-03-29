from google.cloud import bigquery

query_template = """
SELECT address, eth_balance FROM `bigquery-public-data.crypto_ethereum.balances`  where address in (
{}
) ORDER BY eth_balance DESC;
"""

creators_of_ephemeral_contracts = set()
creators_of_redeployed_addrs = set()
reinited_addresses = set()
ephemeral_addrs = set() # TODO check these should all be zero

with open("analysis-results/london-to-present/creators-of-ephemeral-contracts.csv", "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        parts = line.split(',')
        if parts[0] in creators_of_ephemeral_contracts:
            raise Exception("repeating address")

        creators_of_ephemeral_contracts.add(parts[0])

with open("analysis-results/london-to-present/creators-of-redeployed-addrs.csv", "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        parts = line.split(',')
        if parts[0] in creators_of_redeployed_addrs:
            raise Exception("repeating address")

        creators_of_redeployed_addrs.add(parts[0])

with open("analysis-results/london-to-present/redeployed-addrs.csv", "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        parts = line.split(',')
        if parts[0] in reinited_addresses:
            raise Exception("repeating address")

        reinited_addresses.add(parts[0])

with open("analysis-results/london-to-present/ephemeral-addrs.csv", "r") as f:
    lines = f.readlines()[1:]
    for line in lines:
        addr = line.strip(",").strip("\n")
        if addr in ephemeral_addrs:
            raise Exception("repeated address")

        ephemeral_addrs.add(addr)

target_addrs = list(creators_of_ephemeral_contracts) + list(creators_of_redeployed_addrs) + list(reinited_addresses) + list(ephemeral_addrs)

balances = {}

for i in range(0, len(target_addrs), 20000):
    query_addrs = ",".join(["\"" + addr + "\"" for addr in target_addrs[i:i+1000]])
    query = query_template.format(query_addrs)

    # Construct a BigQuery client object.
    client = bigquery.Client()

    print("query for accounts {}..{}".format(i, i + 20000))
    query_job = client.query(query)  # Make an API request.

    for row in query_job:
        balances[row['address']] = int(row['eth_balance']) / 10e17

print("\n".join(["{},{}".format(addr, balance) for addr, balance in balances.items()]))
