#! /usr/bin/env bash
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/credentials.json
python3 pull_trace_data.py
