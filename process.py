import itertools
import functools
import glob

reincarnations = {}
ephemerals = {}
selfdestructed = set()
created = set()
total_lines = 0

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

    @staticmethod
    def FromCSVLine(s: str):
        parts = s.split(',')

        if len(parts) != 10:
            raise Exception("wrong length")

        block_number = int(parts[0])
        tx_hash = parts[2]
        tx_index = int(parts[3])
        trace_id = parse_trace_id(parts[4])
        sender = parts[5]
        receiver = parts[6]
        typ = parts[7]
        status = int(parts[8])
        calltype = None# parts[8]

        return MessageCall(block_number, tx_hash, tx_index, trace_id, sender, receiver, typ, status, calltype)

    def ToCSVLine(self):
        return "{},{},{},{},{},{},{}".format(self.tx_hash, self.tx_index, self.sender, self.sender, self.trace_id, self.call_type, self.type, self.status)

tx_calls = []
tx_created = set()
tx_selfdestructed = set()
tx_ephemerals = set() 

def process_transaction():
    global tx_calls, tx_created, tx_selfdestructed, tx_ephemerals
    global reincarnations, ephemerals, selfdestructed, created

    # sort calls
    if len(tx_calls) > 1:
        tx_calls = sort_tx_calls(tx_calls)

    for call in tx_calls:
        if call.status == 0:
            continue

        if call.type == 'create':
            # TODO what happens to self-destruct inside of create ?
            tx_created.add(call.receiver)
        else: # call is selfdestruct
            if not call.sender in tx_selfdestructed and not call.sender in tx_ephemerals:
                if call.sender in tx_created:
                    tx_ephemerals.add(call.sender)
                    tx_created.remove(call.sender)
                else:
                    tx_selfdestructed.add(call.sender)
    for address in tx_created:
        if address in created:
            import pdb; pdb.set_trace()
            raise Exception("address created twice without being deleted: {0}".format(address))
        if address in selfdestructed:
            selfdestructed.remove(address)
            if address in reincarnations:
                reincarnations[address] += 1
            else: 
                reincarnations[address] = 1
        created.add(address)

    for address in tx_selfdestructed:
        if address == "0x82970e56d1b4aa2af1f90be3347afe87c8859d16":
            import pdb; pdb.set_trace()
            foo = 'bar'

        if address in selfdestructed:
            import pdb; pdb.set_trace()
            raise Exception("address selfdestructed twice without being resurected in-between: {0}".format(address))

        if address in created:
            created.remove(address)

        selfdestructed.add(address)

    for address in tx_ephemerals:
        if not address in ephemerals:
            ephemerals[address] = 1
        else:
            ephemerals[address] += 1

    tx_calls = []
    tx_created = set()
    tx_selfdestructed = set()
    tx_ephemerals = set() 

def process_txs_before_trace(trace_line, start_block, break_block):
    pass

def consume_line(line, start_block, break_block):
    global last_call, created, ephemerals, reincarnations, selfdestructed, tx_calls

    call = MessageCall.FromCSVLine(line)

    if call.block_number < start_block:
        return False
    if call.block_number >= break_block:
        return True

    if len(tx_calls) > 0 and tx_calls[0].tx_hash != call.tx_hash:
        process_transaction()

    tx_calls.append(call)

    return False

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

def main():
    offset = 0

    output_file = open('output.csv', 'w')
    counter = 0
    # start_block=9000000
    start_block= 0 # 9000000
    break_on_block_number = 12799316
    should_break = False

    # txs_lines = open('tx-data.csv', 'r')
    # input_files = sorted(glob.glob("data-traces/*.csv"))
    input_files = ["data-traces/data-000000000181.csv", "data-traces/data-000000000182.csv"]
    # input_files = ["mystery2.csv"]

    for input_file in input_files:
        source_data_file = open(input_file, 'r')
        for line in source_data_file:
            break #read first line (header)

        for line in source_data_file:
            #process_txs_before_trace()

            if consume_line(line, start_block, break_on_block_number):
                should_break = True
                break

            counter += 1
            if counter % 100000 == 0:
                print(advance_progress(), end="\r")

        if should_break:
            break

        print(input_file)
        total_incarnations = 0
        for account, destructed_amt in reincarnations.items():
            total_incarnations += destructed_amt
        print("total contracts ={}".format(total_incarnations + len(created)))

    if not should_break:
        process_transaction()

    import pdb; pdb.set_trace()

if __name__ == "__main__":
    main()
