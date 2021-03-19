import threading
import time
from datetime import datetime
import os
import argparse

TIMEOUT_SEC = 1
TIMESTAMP_PATH = "./timestamp"


def main (**kwargs):
    #Resets the counter to 0 if the command flag is set
    if(kwargs.get("reset_count")):
        write_timestamp(0, 0, write_time=False, write_count=True)
    
    #allow some time for the primary to write the current timestamp before starting the backup
    time.sleep(1)

    print("Backup phase")
    current_count = check_if_primary_exists()
    print("... timed out")

    create_backup()
    
    print("Primary phase")
    print("resuming from {0}".format(current_count))
    run_primary(current_count)


def check_if_primary_exists():
    while True:
        with open(TIMESTAMP_PATH, "r") as f:
            timestamp_line = f.readline()
            count_line = f.readline()

            timestamp = float(timestamp_line)
            current_time = time.time()
            elapsed = current_time - timestamp

            if(elapsed > TIMEOUT_SEC):

                #Exit backup phase with the last recorded count
                current_count = int(count_line)
                return current_count

        time.sleep(0.5)

def run_primary(inital_count):
    count = inital_count
    while True:
        count += 1

        write_timestamp(time.time(), count)

        print(count)
        time.sleep(1)


def write_timestamp(time, count, write_time=True, write_count=True):
    with open(TIMESTAMP_PATH, "r") as file:
        lines = file.readlines()
    if write_time:
        lines[0] = str(time) + "\n"
    if write_count:
        lines[1] = str(count) + "\n"

    with open(TIMESTAMP_PATH, "w") as file:
        for line in lines:
            file.write(line)


def create_backup():
    os.system("start python ./phoenix.py")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process that counts upwards and uses the "process pairs" technique')
    parser.add_argument('-r', action='store_true',
                        help='resets the count to 0 and overrides the existing saved count')

    args = parser.parse_args()
    
    main(reset_count=args.r)