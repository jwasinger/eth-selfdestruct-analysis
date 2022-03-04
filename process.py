import functools

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

        if len(parts) != 8:
            raise Exception("wrong length")

        tx_hash = parts[1]
        tx_index = int(parts[2])
        trace_id = parse_trace_id(parts[3])
        sender = parts[4]
        receiver = parts[5]
        typ = parts[6]
        status = int(parts[7])

        return MessageCall(tx_hash, tx_index, trace_id, sender, receiver, typ, status)

    def ToCSVLine(self):
        return "{},{},{},{},{},{}".format(self.tx_hash, self.tx_index, self.sender, self.sender, self.type, self.status)

last_call = None

def consume_transaction(lines, output_file):
    global last_call, created, ephemerals, reincarnations, selfdestructed

    # TODO read tx_hash of first tx
    calls = []
    tx_created = set()
    tx_selfdestructed = set()
    tx_ephemerals = set() 

    if last_call != None:
        calls = [last_call]

    should_quit = True
    for line in lines:
        should_quit = False

        call = MessageCall.FromCSVLine(line)
        if len(calls) > 0 and call.tx_hash != calls[0].tx_hash:
            # TODO preserve this value for the next call of this function!!!
            # calls = [MessageCall.FromCSVLine(line)]
            last_call = MessageCall.FromCSVLine(line)
            break
        else:
            calls.append(call)

    if should_quit:
        return 0

    if len(calls) == 0:
        return 0
    elif len(calls) > 1:
        calls = sort_tx_calls(calls)


    # for call in calls:
     #   output_file.write(call.ToCSVLine()+"\n")

    # return len(calls)

    # --- 

    # revert of the top-level call, move to the next tx
    if calls[0].status == 0:
        return len(calls)


    for call in calls:
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
        # if exiting a call-frame:
            # if the frame was a create, mark it as created
        # else if entering a call-frame:
            # if the frame is a selfdestruct:
                # if the contract already selfdestructed in this tx:
                    # continue
                # if the contract's address was in created:
                    # remove it from created and add it to ephemerals 
                # else:
                    # add it to deleted
    for address in tx_created:
        if address in created:
            # raise Exception("address created twice without being deleted: {0}".format(address))
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
            # raise Exception("address selfdestructed twice without being resurected in-between: {0}".format(address))
            pass

        if address in created:
            created.remove(address)
        selfdestructed.add(address)

    for address in tx_ephemerals:
        if not address in ephemerals:
            ephemerals[address] = 1
        else:
            ephemerals[address] += 1

    # --- end of transaction: ---
    # for each address in deleted:
        # add to global deleted (shouldn't already be there)
    # for each address in created:
        # if it is in global deleted:
            # add it to reincarnations or increment the incarnation number if it is already there
    # for each address in ephemerals:
        # update the creator ephemeral count

    return len(calls)

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

    source_data_file = open('data.csv', 'r')
    for line in source_data_file:
        break #read first line (header)

    output_file = open('output.csv', 'w')
    counter = 0

    while True:
        lines_read = consume_transaction(source_data_file, output_file)
        offset += lines_read
        counter += 1
        if lines_read == 0:
            break
        if counter % 50000 == 0:
            print(advance_progress(), end="\r")

    # TODO create csv for ephemerals, incarnations
    import pdb; pdb.set_trace()
    foo = 'bar'

if __name__ == "__main__":
    main()
