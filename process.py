reincarnations = {}
ephemerals = {}
deleted = {}

def parse_callstack(callstack_field: str) -> [str]:
    pass

def parse_tx_index(tx_index_field: str) -> int:
    splitted = tx_index_field.split('_')[2:]
    splitted = map(lambda x: int(x), splitted)
    return splitted

def sort_tx_calls(calls):
    max_call_depth = 1
    for call in calls:
        if len(calls.tx_id) > max_call_depth:
            max_call_depth = len(calls.tx_id)

    def score_fn(call) -> int:
        score = 0
        for i in range(len(call.call_id)):
            score += call.call_id * 10**(max_call_depth - i)
        return score

    def sort_fn(x, y) -> int:
        return score_fn(x.call_id) < score_fn(y.call_id)

    return sorted(lambda x,y: sort_fn(x,y), calls)

class MessageCall():
    def __init__(self, status, typ, sender, receiver, tx_index, call_depth):
        self.status = status
        self.type = typ 
        self.sender = sender
        self.receiver = receiver
        self.tx_id = tx_id
        self.call_depth = call_depth

    def FromCSVLine(s: str) -> Self:
        parts = s.split(',')

        if len(parts) != 5:
            raise Exception("wrong length")

        status = parts[0]
        sender = parts[1]
        receiver = parts[2]
        
        tx_index = parse_tx_index(parts[4])

        return MessageCall(status, sender, receiver, callstack, tx_index)

def consume_transaction(lines):
    # TODO read tx_hash of first tx
    calls = []

    for line in lines[1:]:
        tx_hash = parse_tx_hash(line)
        if tx_hash != first_tx_hash:
            break
        else:
            calls.append(line)

    if len(txs) > 1:
        # order txs

    # revert of the top-level call, move to the next tx
    if calls[0]['status'] == '1':
        return len(txs)


    for call in calls:
        # if the call failed, continue

        # TODO what happens to self-destruct inside of create ?

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
    # --- end of transaction: ---
    # for each address in deleted:
        # add to global deleted (shouldn't already be there)
    # for each address in created:
        # if it is in global deleted:
            # add it to reincarnations or increment the incarnation number if it is already there
    # for each address in ephemerals:
        # update the creator ephemeral count

    return len(txs)

def main():
    csv_lines = readlines() 

    if len(csv_lines) == 0:
        return

    while offset < len(csv_lines):
        lines_read = consume_transaction(csv_lines[offset:])
        offset += lines_read

    # TODO create csv for ephemerals, incarnations
