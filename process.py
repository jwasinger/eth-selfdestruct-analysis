reincarnations = {}
ephemerals = {}
deleted = {}

class MessageCall():
    def __init__(self, status, typ, sender, receiver, callstack):
        self.status = status
        self.type = typ 
        self.sender = sender
        self.receiver = receiver
        self.callstack = callstack 
        self.tx_index = tx_index

    def FromCSVLine(s: str) -> Self:
        status = ''
        sender = ''
        receiver = ''
        callstack = []
        tx_index = 0

        # TODO parse

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

    # revert of the top-level call, move to the next tx
    if calls[0]['status'] == '1':
        return len(txs)

    if len(txs) > 1:
        # order txs

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
