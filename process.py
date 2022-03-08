import functools
import glob

reincarnations = {}
ephemerals = {}
selfdestructed = set()
created = set()
total_lines = 0

def sort_tx_calls(calls):
    max_call_depth = 1
    for call in calls:
        if len(call.trace_id) > max_call_depth:
            max_call_depth = len(call.trace_id)

    def score_fn(trace_id) -> int:
        score = 0
        for i in range(len(trace_id)):
            score += trace_id[i] * 10**(max_call_depth - i)
        return score

    def sort_fn(x, y) -> int:
        if score_fn(x.trace_id) < score_fn(y.trace_id):
            return -1
        else:
            return 1

    return sorted(calls, key=functools.cmp_to_key(sort_fn))

def parse_trace_id(s: str):
    parts = s.split('_')[2:]
    parts = [part for part in parts if part != '']
    parts = [int(part) for part in parts]

    if len(parts) == 0:
        parts = [0]
    return parts

class MessageCall():
    def __init__(self, tx_hash, tx_index, trace_id, sender, receiver, typ, status):
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.trace_id = trace_id
        self.sender = sender
        self.receiver = receiver
        self.type = typ
        self.status = status

    @staticmethod
    def FromCSVLine(s: str):
        parts = s.split(',')

        if len(parts) != 10:
            raise Exception("wrong length")

        tx_hash = parts[2]
        tx_index = int(parts[3])
        trace_id = parse_trace_id(parts[4])
        sender = parts[5]
        receiver = parts[6]
        typ = parts[7]
        status = int(parts[8])

        return MessageCall(tx_hash, tx_index, trace_id, sender, receiver, typ, status)

    def ToCSVLine(self):
        return "{},{},{},{},{},{}".format(self.tx_hash, self.tx_index, self.sender, self.sender, self.type, self.status)

tx_calls = []
tx_created = set()
tx_selfdestructed = set()
tx_ephemerals = set() 

def process_transaction():
    global tx_calls, tx_created, tx_selfdestructed, tx_ephemerals
    global reincarnations, ephemerals, selfdestructed, created

    # sort calls
    if len(tx_calls) > 1:
        sort_tx_calls(tx_calls)

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
            raise Exception("address created twice without being deleted: {0}".format(address))
            #print("address created twice without being deleted: {0}".format(address))
            pass
        if address in selfdestructed:
            selfdestructed.remove(address)
            if address in reincarnations:
                reincarnations[address] += 1
            else: 
                reincarnations[address] = 1
        created.add(address)

    for address in tx_selfdestructed:
        if address in selfdestructed:
            raise Exception("address selfdestructed twice without being resurected in-between: {0}".format(address))
            pass

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

def consume_line(line):
    global last_call, created, ephemerals, reincarnations, selfdestructed, tx_calls

    call = MessageCall.FromCSVLine(line)

    if len(tx_calls) > 0 and tx_calls[0].tx_hash != call.tx_hash:
        process_transaction()
    else:
        tx_calls.append(call)

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

    input_files = sorted(glob.glob("data/*.csv"))
    for input_file in input_files:
        source_data_file = open(input_file, 'r')
        for line in source_data_file:
            break #read first line (header)

        for line in source_data_file:
            consume_line(line)
            counter += 1
            if counter % 10000 == 0:
                print(advance_progress(), end="\r")

        print("ephemerals length = {}".format(len(ephemerals)))
        print("selfdestructed length ={}".format(len(selfdestructed)))
        import pdb; pdb.set_trace()
        foo = 'bar'

    process_transaction()

if __name__ == "__main__":
    main()
