#!/usr/bin/python3

import json
import time
import argparse
from builtins import function
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tool to merge two sorted logs.")

    parser.add_argument(
        "log_a_path",
        metavar="<LOG_A PATH>",
        type=str,
        help="path to file - log1",
    )

    parser.add_argument(
        "log_b_path",
        metavar="<LOG_B PATH>",
        type=str,
        help="path to file - log2",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="<MERGED_LOG PATH>",
        type=str,
        action="store",
        help="path to file with merged logs",
        dest="output_path",
    )

    return parser.parse_args()


def _sort_logs(log_a_path: Path, log_b_path: Path, _on_next: function) -> None:
    print(f"merging {log_a_path} and {log_b_path}...")

    with open(log_a_path, "r") as log_a, open(log_b_path, "r") as log_b:

        record_a, timestamp_a = _next_record(log_a)
        record_b, timestamp_b = _next_record(log_b)

        while record_a or record_b:
            if record_a and (not record_b or timestamp_a <= timestamp_b):
                _on_next(record_a)
                record_a, timestamp_a = _next_record(log_a)
            elif record_b and (not record_a or timestamp_b < timestamp_a):
                _on_next(record_b)
                record_b, timestamp_b = _next_record(log_b)


def _next_record(log_filename):
    line = log_filename.readline()
    if line:
        record = json.loads(line)
        return record, record.get("timestamp")
    else:
        return None, None


def _merge_logs(on_next, args):
    log_a_dir = Path(args.log_a_path)
    log_b_dir = Path(args.log_b_path)
    _sort_logs(log_a_dir, log_b_dir, on_next)


def main() -> None:

    t0 = time.time()
    args = _parse_args()
    if args.output_path:
        with open(args.output_path, "w") as output:

            def _write_to_file(record):
                json.dump(record, output)
                output.write("\n")

            _merge_logs(_write_to_file, args)
    else:
        _merge_logs(print, args)

    print(f"finished in {time.time() - t0:0f} sec")


if __name__ == "__main__":
    main()
