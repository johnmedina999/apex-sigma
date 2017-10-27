import os
from time import time
from datetime import datetime as date
import logging

log_fmt = '%(levelname)-8s %(asctime)s %(name)-20s %(message)s'

if os.getenv('LOGTARGET_JOURNAL'):
    log_fmt = '%(levelname)-8s %(name)-20s %(message)s'

log_dir = 'log'

if not os.path.exists(log_dir):
    os.mkdir(log_dir)

logfile_name = date.fromtimestamp(time()).strftime('%Y%m%d-%H%M%S') + '.log'
log_file = os.path.join(log_dir, logfile_name)

formatter = logging.Formatter(log_fmt)


def create_logger(name):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    return logger

def get_logs(last_amount):
    with open(log_file) as fp:
        return tail(fp, last_amount)

# Thanks https://stackoverflow.com/a/13790289
"""Tail a file and get X lines from the end"""
def tail(f, lines=1, _buffer=4098):    
    lines_found = []         # place holder for the lines found   
    block_counter = -1       # block counter will be multiplied by buffer to get the block size from the end

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:      # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()
        block_counter -= 1   # decrement the block counter to get the next X bytes
    
    return lines_found[-lines:]