import argparse
from dune.loader import load
from dune.process import process_dune
from llm.writer import write_thread
from graphing.graph import Grapher
from pathlib import Path
import datetime
import time
import os
import pickle
from llm.blocks import BlockWriter
from dotenv import load_dotenv
import glob
import zipfile
import io
import requests


def main(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    sol_start_deposits: float,
    sol_end_deposits: float,
):
    start_time = time.time()  # start timing
    dune_loaded = load(str(start_date), str(end_date), sol_start_deposits, sol_end_deposits)
    # dune_loaded = pickle.load(open('data/dune_data_2023-08-07_11-36.pkl', 'rb'))
    processed = process_dune(dune_loaded)

    writer = BlockWriter(str(end_date), str(start_date))
    thread = writer.compose_thread(processed)
    print(thread)

    print("Writing thread to file")
    Path(f"threads/{str(end_date)}").mkdir(parents=True, exist_ok=True)
    with open(f"threads/{str(end_date)}/thread.md", "w") as f:
        f.write(thread)
    print(f"Wrote thread to file in threads/{end_date}/thread.md")

    print("Graphing")
    grapher = Grapher(str(end_date))
    print(dune_loaded["totalStEthInDeFi"])
    grapher.process_all(dune_loaded)
    print(f"Done Graphing. Graphs are saved in graphs/{end_date} folder")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    print("Delivering Email")
    files = create_files(end_date)

    response = requests.post(os.environ['MAKE_WEBHOOK_URL'], files=files)
    return

def create_files(end_date):
    thread_file_path = f"threads/{end_date}/thread.md"
    graph_files_paths = glob.glob(f"graphs/{end_date}/*")

    # Adding the thread.md file
    files = {'thread': (os.path.basename(thread_file_path), open(thread_file_path, 'rb'), 'text/markdown')}

    # Adding the .png files
    for i, file_path in enumerate(graph_files_paths):
        files[f'graph_{i}'] = (os.path.basename(file_path), open(file_path, 'rb'), 'image/png')

    return files


if __name__ == "__main__":
    load_dotenv()
    if os.environ.get("DUNE_API_KEY") is None:
        print("Please set DUNE_API_KEY environment variable")
        exit(1)

    if os.environ.get("OPENAI_API_KEY") is None:
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)

    if os.environ.get("MAKE_WEBHOOK_URL") is None:
        print("Please set MAKE_WEBHOOK_URL environment variable")
        exit(1)

    parser = argparse.ArgumentParser(description="Lido Weekly Digest Helper")
    parser.add_argument(
        "-sd",
        "--start_date",
        type=str,
        required=False,
        help="Description for start_date argument in %Y-%m-%d format",
    )
    parser.add_argument(
        "-ed",
        "--end_date",
        type=str,
        required=False,
        help="Description for end_date argument in %Y-%m-%d format",
    )

    args = parser.parse_args()

    # convert start date and ed to datetime objects

    if (args.start_date or args.end_date) is None:
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        end_date = datetime.datetime.now() - datetime.timedelta(days=1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)        
    else:
        start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")

    print(f"start_date: {str(start_date)}")
    print(f"end_date: {str(end_date)}")

    main(start_date, end_date, 0, 0)
