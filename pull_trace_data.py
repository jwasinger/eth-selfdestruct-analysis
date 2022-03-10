from process import MessageCall
from google.cloud import bigquery
import functools
import itertools
import os

query_template = """
select block_number, transaction_hash, transaction_index, trace_id, from_address, to_address, trace_type, call_type, status, subtraces from `bigquery-public-data.crypto_ethereum.traces`
    where block_timestamp > timestamp(DATE_ADD(DATE "2015-07-30", INTERVAL {start_day} DAY)) and  block_timestamp < timestamp(DATE_ADD(DATE "2015-07-30", INTERVAL {end_day} DAY))
    and (trace_type='suicide' or trace_type = 'create' or trace_type = 'delegatecall' or trace_type = 'callcode')
        order by block_number asc, transaction_index asc
"""


def main():
    output_data_folder = "chain_trace_data"
    start_time = ''
    end_time = ''
    time_interval = 3600 * 24 # grab data in 1-day intervals

    # if output_data_folder exists:
        # open source data folder and note latest file
    # else:
        # create output_data_folder

    # continue grabbing data until we reach the end time

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

def query_trace_data_and_format_results(client, start_day):
    result = []
    query_job = client.query(query_template.format(start_day=start_day, end_day=start_day + 1))
    for row in query_job:
        result.append(MessageCall.FromQueryResultRow(row))
    return iter(result)

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

        for row_trace in query_rows:
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

def write_trace_results(output_dir, start_time, traces):
    with open(os.path.join(output_dir, "call_traces_{0}.txt".format(start_time)), 'w') as f:
        for trace in traces:
            f.write(MessageCall.ToCSVLine(trace))

client = bigquery.Client()
day = 0
while True:
    calls = query_trace_data_and_format_results(client, day)
    tx_reader = TransactionReader()
    
    full_day_calls = []
    print("new day ", day)
    while True:
        tx_calls = tx_reader.ReadNextTransaction(calls)
        if len(tx_calls) == 0:
            break

        full_day_calls += tx_calls

    write_trace_results("output", day, full_day_calls)

    day += 1
