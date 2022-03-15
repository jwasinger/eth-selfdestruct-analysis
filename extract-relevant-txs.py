import os
import glob
from process import TransactionReader, MessageCall

class TargetTransactionReader:
    def __init__(self):
        self.last_trace = None

    def ReadNextTransactionTraces(self, csv_rows) -> [str]:
        should_keep = False
        tx_traces = []
        first_trace = None
        if self.last_trace != None:
            first_trace = self.last_trace
            tx_traces.append(first_trace)
            self.last_trace = None

        for row in csv_rows:
            if first_trace == None:
                first_trace = row
                tx_traces.append(first_trace)
                continue

            parts = row.split(",")
            if parts[1] !=  first_trace.split(",")[1]:
                self.last_trace = row
                break

            if parts[4][:6] == "create" or parts[4][:8] == "suicide":
                should_keep = True
            tx_traces.append(row)

        if len(tx_traces) == 0:
            return None

        if not should_keep:
            return []
        else:
            return tx_traces

class OutputWriter:
    def __init__(self):
        self.output_dir = "sanitized-data"
        self.cur_output_idx = 0
        self.cur_output_file = None
        self.cur_output_file_written = 0
        self.max_output_file_size = 100000000

    def WriteTraces(self, traces: [MessageCall]):
        print(self.cur_output_file_written)
        if self.cur_output_file == None:
            output_filename = "data-sanitized-"+str(self.cur_output_idx).rjust(8, '0')+".csv"
            self.cur_output_file = open(os.path.join(os.getcwd(), self.output_dir, output_filename), 'w')

        if self.cur_output_file_written >= self.max_output_file_size:
            self.cur_output_file.close()
            self.cur_output_idx += 1
            new_output_filename = "data-sanitized-"+str(self.cur_output_idx).rjust(8, '0')+".csv"
            print("writing new file {}".format(new_output_filename))
            self.cur_output_file = open(os.path.join(os.getcwd(), self.output_dir, new_output_filename), 'w')
            self.cur_output_file_written = 0

        for trace_str in traces:
            self.cur_output_file.write(trace_str + "\n")
            self.cur_output_file_written += len(trace_str)

    def Close(self):
        if self.cur_output_file:
            self.cur_output_file.close()

input_files = sorted(glob.glob("data-traces/*.csv"))
t = TargetTransactionReader()
output_writer = OutputWriter()

for input_file in input_files:
    source_data_file = open(input_file, 'r')
    for line in source_data_file: # skip first line
        break

    while True:
        tx_calls = t.ReadNextTransactionTraces(source_data_file)
        if tx_calls == None:
            break
        if len(tx_calls) != 0:
            output_writer.WriteTraces(tx_calls)
