import itertools
import functools
import glob

total_created = 0
total_selfdestructed = 0

def sort_tx_calls(calls):
    def sort_fn(x, y) -> int:
        for t1, t2 in itertools.zip_longest(x.trace_id, y.trace_id):
            if t2 == None:
                return 1
            elif t1 == None:
                return -1

            if t1 > t2:
                return 1
            elif t1 < t2:
                return -1
        return 0

    return sorted(calls, key=functools.cmp_to_key(sort_fn))

def parse_trace_id(s: str):
    parts = s.split('_')[2:]
    parts = [part for part in parts if part != '']
    parts = [int(part) for part in parts]

    if len(parts) == 0:
        parts = [0]
    return parts

class MessageCall():
    def __init__(self, block_number, tx_hash, tx_index, trace_id, sender, receiver, typ, status, call_type):
        self.block_number = block_number
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.trace_id = trace_id
        self.sender = sender
        self.receiver = receiver
        self.type = typ
        self.status = status
        self.call_type=call_type
        self.call_depth = len(trace_id) - 1
        self.parent_call = None

    @staticmethod
    def FromCSVLine(s: str):
        parts = s.strip('\n').split(',')

        if len(parts) != 10:
            raise Exception("wrong length")

        block_number = int(parts[3])
        tx_hash = parts[1]
        tx_index = int(parts[4])
        trace_id = parse_trace_id(parts[2])
        sender = parts[5]
        receiver = parts[6]
        typ = parts[7]
        status = int(parts[9])
        calltype = parts[8]

        return MessageCall(block_number, tx_hash, tx_index, trace_id, sender, receiver, typ, status, calltype)

    def ToCSVLine(self):
        return "{},{},{},{},{},{},{}".format(self.tx_hash, self.tx_index, self.sender, self.sender, self.trace_id, self.call_type, self.type, self.status)

def find_direct_parent(call, tx_calls) -> MessageCall:
    return None
    for c in reversed(tx_calls):
        if c.call_depth == call.call_depth - 1 and c.trace_id == call.trace_id[:-1]:
            return c

    return None

class TransactionReader:
    def __init__(self):
        self.last_trace = None

    # TODO this is broken in the case where a transaction straddles two files
    def ReadNextTransaction(self, query_rows, link_txs=True) -> [MessageCall]:
        tx_traces = []
        first_trace = None
        if self.last_trace != None:
            first_trace = self.last_trace
            tx_traces.append(first_trace)
            self.last_trace = None

        for idx, row in enumerate(query_rows):
            row_trace = MessageCall.FromCSVLine(row)

            if first_trace == None:
                first_trace = row_trace
                tx_traces.append(first_trace)
                continue
                
            if first_trace.tx_hash != row_trace.tx_hash:
                self.last_trace = row_trace
                break

            if link_txs:
                row_trace.parent_call = find_direct_parent(row_trace, tx_traces)
            tx_traces.append(row_trace)

        if len(tx_traces) > 1:
            tx_traces = sort_tx_calls(tx_traces)

        return tx_traces

class AnalysisState:
    def __init__(self):
        self.ephemerals = {}
        self.reincarnations = {}
        self.selfdestructed = set()
        self.created = set()

        # map of contract address -> address of contract that created it
        self.creators = {}

    def ApplyTransactionCalls(self, tx_calls: [MessageCall]):
        global total_created
        global total_selfdestructed

        tx_created = set()
        tx_selfdestructed = set()
        tx_ephemerals = set() 

        for call in tx_calls:

            if call.status == 0:
                continue

            if call.type == 'create':
                if call.parent_call != None:
                    if call.parent_call.type == 'delegatecall' or call.parent_call.type == 'callcode':
                        import pdb; pdb.set_trace()

                total_created += 1
                if call.receiver in tx_created:
                    raise Exception("the same contract cannot be created twice during the same transaction")

                # TODO what happens to self-destruct inside of create ?
                tx_created.add(call.receiver)
                if not call.receiver in self.creators:
                    self.creators[call.receiver] = call.sender
            elif call.type == 'suicide': # call is selfdestruct
                total_selfdestructed += 1
                if not call.sender in tx_selfdestructed and not call.sender in tx_ephemerals:
                    if call.sender in tx_created:
                        tx_ephemerals.add(call.sender)
                        tx_created.remove(call.sender)
                    else:
                        tx_selfdestructed.add(call.sender)

                if call.sender in tx_ephemerals:
                    if not call.sender in self.creators:
                        raise Exception("ephemeral address should have been in created map")
            elif call.type == 'call':
                if call.call_type == 'delegatecall':
                    pass
                elif call.call_type == 'callcode':
                    pass
                else:
                    import pdb; pdb.set_trace()
                    raise Exception("unexpected call type {}".format(call.call_type))
            elif call.type == None:
                import pdb; pdb.set_trace()
                raise Exception("unexpected trace type {}".format(call.type))
        for address in tx_created:
            if address in self.created:
                import pdb; pdb.set_trace()
                raise Exception("address created twice without being deleted: {0}".format(address))
            if address in self.selfdestructed:
                self.selfdestructed.remove(address)
                if address in self.reincarnations:
                    self.reincarnations[address] += 1
                else: 
                    self.reincarnations[address] = 1
            self.created.add(address)

        for address in tx_selfdestructed:
            if address in self.selfdestructed:
                import pdb; pdb.set_trace()
                raise Exception("address selfdestructed twice without being resurected in-between: {0}".format(address))

            if address in self.created:
                self.created.remove(address)

            #if not address in self.creators:
                #raise Exception("selfdestructed address should have been in creators map")
            #del self.creators[address]

            self.selfdestructed.add(address)

        for address in tx_ephemerals:
            if not address in self.ephemerals:
                self.ephemerals[address] = 1
            else:
                self.ephemerals[address] += 1

progress_str = "_.."
def advance_progress():
    global progress_str

    if progress_str == "_..":
        progress_str = "._."
    elif progress_str == "._.":
        progress_str = ".._"
    elif progress_str == ".._":
        progress_str = "_.."

    return progress_str

def do_analysis():
    output_file = open('output.csv', 'w')
    counter = 0
    should_break = False

    # run post-london only
    input_files = sorted(glob.glob("data-traces/*.csv"))
    start_block= 12965000
    break_on_block_number = 999999999999999999999999 

    # settings to run against all chain history up to previous analysis:
    # https://nbviewer.org/github/adompeldorius/selfdestruct-analysis/blob/main/analysis.ipynb
    #input_files = sorted(glob.glob("data-traces-all/*.csv"))
    #start_block= 0
    #break_on_block_number = 12799316

    analysis_state = AnalysisState()

    t = TransactionReader()

    for input_file in input_files:
        source_data_file = open(input_file, 'r')
        for line in source_data_file:
            break

        print("analyzing {}".format(input_file))

        while True:
            tx_calls = t.ReadNextTransaction(source_data_file)
            if len(tx_calls) == 0:
                break

            if tx_calls[0].block_number < start_block:
                continue

            if tx_calls[0].block_number >= break_on_block_number:
                should_break = True
                break

            analysis_state.ApplyTransactionCalls(tx_calls)

            counter += 1
            if counter % 1000 == 0:
                print(advance_progress(), end="\r")

        if should_break:
            break

    return analysis_state


if __name__ == "__main__":
    analysis_result = do_analysis()
    ephemeral_creators = {}

    for address, num_ephemerals in analysis_result.ephemerals.items():
        if not address in analysis_result.creators:
            raise Exception("missing creator for ephemeral address {}".format(address))

        creator = analysis_result.creators[address]
        if not creator in ephemeral_creators:
            ephemeral_creators[creator] = num_ephemerals
        else:
            ephemeral_creators[creator] += num_ephemerals

    reincarnated_creators = {}
    for address, num_incarnations in analysis_result.reincarnations.items():
        creator = ''
        if not address in analysis_result.creators:
            import pdb; pdb.set_trace()
            fuck = True

        creator = analysis_result.creators[address]
        if not creator in reincarnated_creators:
            reincarnated_creators[creator] = num_incarnations
        else:
            reincarnated_creators[creator] += num_incarnations

    import pdb; pdb.set_trace()
    with open("analysis-results/creators-of-ephemeral-contracts.csv", "w") as f:
        f.write("creator contract address, number of ephemeral contracts created\n")

        for creator, num_ephemerals in ephemeral_creators.items():
            f.write("{}, {}\n".format(creator, num_ephemerals))

    with open("analysis-results/creators-of-redeployed-addrs.csv", "w") as f:
        f.write("creator contract address, number of child contracts that were redeployed\n")

        for creator, num_redeployed in reincarnated_creators.items():
            f.write("{}, {}\n".format(creator, num_redeployed))
