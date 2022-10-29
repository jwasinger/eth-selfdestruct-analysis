from google.cloud import bigquery

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
    parts = [0] + [int(part) for part in parts]

    if len(parts) == 0:
        parts = [0]
    return parts

class MessageCall():
    def __init__(self, block_number=None, tx_hash=None, tx_index=None, trace_id=None, sender=None, receiver=None, trace_type=None, status=None, call_type=None, value=None):
        self.block_number = block_number
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.trace_id = parse_trace_id(trace_id)
        self.sender = sender
        self.receiver = receiver
        self.trace_type = trace_type
        self.call_type=call_type
        self.status = status
        self.call_depth = len(trace_id) - 1
        self.parent_call = None
        self.value = value

class AnalysisState():
    def __init__(self):
        # store contracts modified in the tx in a set
        # apply them to the db at the end of the tx
        self.tx_contracts = {}

    def __get_contract(self, address):
        if address in self.tx_contracts:
            return self.tx_contracts[address]

        # TODO try to look it up in the database

        # TODO return None (it doesn't exist)

    def ApplyTxCalls(self, tx_calls):
        self.tx_contracts = {}
        if len(tx_calls) = 0:
            return

        for call in tx_calls:
            if call.status == 0:
                continue

            if call.type == 'create':
                # create or update the contract object in the tx-scope contract set
                pass
            elif call.type == 'suicide':
                pass
            elif call.type == 'call':
                pass

def do_query():
    client = bigquery.Client()

    # Perform a query.
    QUERY = '''
    SELECT block_hash, transaction_hash,  trace_id, block_number, transaction_index, from_address, to_address, trace_type, call_type, status, value FROM `bigquery-public-data.crypto_ethereum.traces` 
        WHERE block_timestamp > \'2016-05-01\' and block_timestamp < \'2016-05-02\'
        ORDER BY block_number ASC, transaction_index ASC
    '''

    query_job = client.query(QUERY, project="geth-team")  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        yield MessageCall(
                block_number=row.get('block_number'),
                tx_hash=row.get('transaction_hash'),
                tx_index=row.get('transaction_index'),
                trace_id=row.get('trace_id'),
                sender=row.get('from_address'),
                receiver=row.get('to_address'),
                call_type=row.get('call_type'),
                trace_type=row.get('trace_type'),
                status=row.get('status'),
                value=row.get('value'))

def analyze(query_rows):
    cur_tx_hash = None
    tx_calls = []

    for row in query_rows:
        import pdb; pdb.set_trace()
        if row.trace_type == 'reward':
            continue

        if row.tx_hash != cur_tx_hash:
            analysis_state.ApplyTx(tx_calls)
            tx_calls = [row]
            cur_tx_hash = tx_hash
        else:
            tx_calls.append(row)

    analysis_state.ApplyTx(tx_calls)

if __name__ == "__main__":
        analyze(do_query())
