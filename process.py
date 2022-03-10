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

    @staticmethod
    def FromQueryResultRow(row):
        block_number = row['block_number']
        tx_hash = row['transaction_hash']
        tx_index = row['transaction_index']
        trace_id = row['trace_id']
        sender = row['from_address']
        receiver = row['from_address']
        
        call_type = None
        if row['trace_type'] == 'call':
            call_type = row['call_type']

        trace_type= row['trace_type']
        status = row['status']
        
        return MessageCall(block_number, tx_hash, tx_index, trace_id, sender, receiver, trace_type, status, call_type)

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

class TransactionReader:
    def __init__(self):
        self.last_trace = None

    def ReadNextTransaction(self, query_rows) -> [MessageCall]:
        tx_traces = []
        first_trace = None
        if self.last_trace != None:
            first_trace = self.last_trace
            tx_traces.append(first_trace)
            self.last_trace = None

        for row in query_rows:
            row_trace = MessageCall.FromCSVLine(row)

            if first_trace == None:
                first_trace = row_trace
                tx_traces.append(first_trace)
                continue
                
            if first_trace.tx_hash != row_trace.tx_hash:
                self.last_trace = row_trace
                break
            else:
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
                total_created += 1
                # TODO what happens to self-destruct inside of create ?
                tx_created.add(call.receiver)
            else: # call is selfdestruct
                total_selfdestructed += 1
                if not call.sender in tx_selfdestructed and not call.sender in tx_ephemerals:
                    if call.sender in tx_created:
                        tx_ephemerals.add(call.sender)
                        tx_created.remove(call.sender)
                    else:
                        tx_selfdestructed.add(call.sender)
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
            if address == "0x82970e56d1b4aa2af1f90be3347afe87c8859d16":
                import pdb; pdb.set_trace()
                foo = 'bar'

            if address in self.selfdestructed:
                import pdb; pdb.set_trace()
                raise Exception("address selfdestructed twice without being resurected in-between: {0}".format(address))

            if address in self.created:
                self.created.remove(address)

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

def main():
    offset = 0

    output_file = open('output.csv', 'w')
    counter = 0
    # start_block=9000000
    start_block= 0 # 9000000
    break_on_block_number = 12799316
    should_break = False

    # txs_lines = open('tx-data.csv', 'r')
    input_files = sorted(glob.glob("data-traces/*.csv"))
    # input_files = ["data-traces/data-000000000181.csv", "data-traces/data-000000000182.csv"]
    # input_files = ["mystery2.csv"]
    analysis_state = AnalysisState()

    for input_file in input_files:
        source_data_file = open(input_file, 'r')
        for line in source_data_file:
            break #read first line (header)

        print(input_file)
        print(total_created)
        print(total_selfdestructed)

        while True:
            t = TransactionReader()
            tx_calls = t.ReadNextTransaction(source_data_file)
            if len(tx_calls) == 0:
                break

            if tx_calls[0].block_number >= break_on_block_number:
                should_break = True
                break

            analysis_state.ApplyTransactionCalls(tx_calls)

            counter += 1
            if counter % 1000 == 0:
                print(advance_progress(), end="\r")

        if should_break:
            break


    if not should_break:
        process_transaction()


if __name__ == "__main__":
    main()
