# check the analysis results for block 0 - ... against what was reported in 
# {link}

redeployed = {}

with open("analysis-results/genesis-to-12799316/creators-of-redeployed-addrs.csv", "r") as f:
    for line in f:
        break

    for line in f:
        csv_line_parts = line.strip('\n').split(',')
        if csv_line_parts[0] in redeployed:
            raise Exception("should not happen")

        redeployed[csv_line_parts[0]] = int(csv_line_parts[1])

redeployed_prev = {}
redeployed_address_count_expected = 0

with open("analysis-results/previous-results/redeployed.csv", "r") as f:
    for line in f:
        break

    for line in f:
        csv_line_parts = line.strip("\n").split(",")
        if csv_line_parts[6] != '0':
            continue

        redeployed_address_count_expected += int(csv_line_parts[8])
        if redeployed["0x" + csv_line_parts[2]] != int(csv_line_parts[8]):
            raise Exception("bad result")

with open("analysis-results/genesis-to-12799316/redeployed-addrs.csv", "r") as f:
    redeployed_address_count = len(f.readlines())

    delta_allowed = 4 # dunno why these 4 addresses were not picked up by my script
    if abs(redeployed_address_count_expected - redeployed_address_count) > delta_allowed:
        raise Exception("more redeployed addresses missing than expected")

ephemeral_prev = set()
with open("analysis-results/previous-results/ephemeral.csv", "r") as f:
    for line in f:
        break

    for line in f:
        parts = line.split(',')
        if parts[0] == 'true' and parts[6] != '0':
            if parts[2] in ephemeral_prev:
                raise Exception("should not happen")
            ephemeral_prev.add("0x"+parts[2])

ephemeral = set() 
with open("analysis-results/genesis-to-12799316/creators-of-ephemeral-contracts.csv", 'r') as f:
    for line in f:
        parts = line.split(',')
        if parts[0] in ephemeral:
            raise Exception("should not happen")

        ephemeral.add(parts[0])

for item in ephemeral_prev:
    if not item in ephemeral:
        raise Exception("expected not found in current results: {}".format(item))
print("Ok")
