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

def consume_transaction(lines):
    global created, ephemerals, reincarnations, selfdestructed

    # TODO read tx_hash of first tx
    calls = []
    tx_created = set()
    tx_selfdestructed = set()
    tx_ephemerals = set() 

    calls = [MessageCall.FromCSVLine(lines[0])]
    if len(lines) > 1:
        for line in lines[1:]:
            call = MessageCall.FromCSVLine(line)
            if call.tx_hash != calls[0].tx_hash:
                break
            else:
                calls.append(call)

        if len(calls) > 1:
            calls = sort_tx_calls(calls)

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
            raise Exception("address created twice without being deleted: {0}".format(address))
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

progress_str = "  ."
def advance_progress():
    global progress_str

    if progress_str == ".  ":
        progress_str = " . "
    elif progress_str == " . ":
        progress_str = "  ."
    elif progress_str == "  .":
        progress_str = ".  "

    return progress_str

def main():
    csv_lines = []
    offset = 0

    with open('data.csv', 'r') as f:
        csv_lines = f.readlines() 

    if len(csv_lines) < 2:
        print("csv has no data")
        return

    # remove header
    csv_lines = csv_lines[1:]
    total_lines = len(csv_lines)

    while offset < len(csv_lines):
        lines_read = consume_transaction(csv_lines[offset:])
        offset += lines_read
        if (total_lines - offset) % 20 == 0:
            print("{0} traces left to analyze".format(total_lines - offset) + advance_progress())#, end='\r')

    # TODO create csv for ephemerals, incarnations
    import pdb; pdb.set_trace()
    foo = 'bar'

if __name__ == "__main__":
    main()
