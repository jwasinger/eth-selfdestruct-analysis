from analyze import MessageCall, TransactionReader, AnalysisState
import glob

def main():
    reused_addrs_creators = set()
    reused_ephemeral_addrs_creators = set()

    with open("analysis-results/london-to-present/creators-of-redeployed-addrs.csv","r") as f:
        for line in f:
            break

        for line in f:
            parts = line.split(",")
            if parts[0] in reused_addrs_creators:
                raise Exception("shouldn't happen")
            reused_addrs_creators.add(parts[0]) 

    with open("analysis-results/london-to-present/ephemeral-creators-which-reuse-addrs.csv","r") as f:
        for line in f:
            break

        for line in f:
            if line.strip('\n') in reused_ephemeral_addrs_creators:
                raise Exception("shouldn't happen")

            reused_ephemeral_addrs_creators.add(parts[0]) 

    creator_value_endowed = {}
    input_files = sorted(glob.glob("data-traces-small-new/*.csv"))
    t = TransactionReader()
    done = False

    start_block=12965000
    end_block=99999999999999999

    for input_file in input_files:
        source_data_file = open(input_file, 'r')
        for line in source_data_file:
            break

        print("analyzing {}".format(input_file))

        while True:
            tx_calls = t.ReadNextTransaction(source_data_file)
            if len(tx_calls) == 0:
                break


            if tx_calls[0].block_number > end_block:
                done = True
                break
            if tx_calls[0].block_number < start_block:
                continue

            for call in tx_calls:
                if call.status == 0:
                    continue
                if call.type == 'create':
                    if call.sender in reused_addrs_creators or call.sender in reused_ephemeral_addrs_creators:
                        if not call.sender in creator_value_endowed:
                            creator_value_endowed[call.sender] = int(call.value)
                        else:
                            creator_value_endowed[call.sender] += int(call.value)
        if done:
            break

    import pdb; pdb.set_trace()

if __name__ == "__main__":
    main()
