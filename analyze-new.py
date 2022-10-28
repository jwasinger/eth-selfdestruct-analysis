from google.cloud import bigquery

class MessageCall():
    def __init__(self, block_number, tx_hash, tx_index, trace_id, sender, receiver, typ, status, call_type, value):
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
        self.value = value

    @staticmethod
    def FromQueryRow(row):
        import pdb; pdb.set_trace()
        pass

def do_query():
    client = bigquery.Client()

    # Perform a query.
    QUERY = (
        'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
        'WHERE state = "TX" '
        'LIMIT 100')
    query_job = client.query(QUERY, project="geth-team")  # API request
    rows = query_job.result()  # Waits for query to finish
    import pdb; pdb.set_trace()

    for row in rows:
        yield row

def analyze(query_rows):
    cur_tx_hash = None
    tx_calls = []

    for row in query_rows:
        if row["tx_hash"] != cur_tx_hash:
            analysis_state.ApplyTx(tx_calls)
            tx_calls = [row]
            cur_tx_hash = tx_hash
        else:
            tx_calls.append(row)

    analysis_state.ApplyTx(tx_calls)

if __name__ == "__main__":
        analyze(do_query())
