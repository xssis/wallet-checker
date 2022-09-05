#!/usr/bin/env python3

import datetime
import os, os.path as op
import re
import sys
import argparse
import multiprocessing as mp

from bitcoin2john import check_wallet
from dump_unenc_keys import main_dump

LOG_DIR='./'
BASE_DIR = op.abspath(op.dirname(__file__))
#SOURCE_DIR = op.join(BASE_DIR, '/home/user/FILES/')

SOURCE_DIR = 'C:/logs/'

HASHES_LOG='hashes.txt'
PRIVKEY_LOG='privkeys.txt '

def write_log(log_name, data):
    with open(op.join(LOG_DIR, log_name),'a',encoding='utf-8') as f:
        f.write(str(data)+'\n')

def find_in_file(wallet_path,log_lock,HASHES_LOG,PRIVKEY_LOG):
    try:
        # res=check_wallet(path)
        res = check_wallet(wallet_path)
        if res is None: # it's not valid wallet.dat
            return
        (is_encrypted, wallet_hash_to_brute) = res
        if is_encrypted == 1: #not encrypted
            pk = main_dump(wallet_path)
            if len(pk) > 0:
                log_lock.acquire()
                try:
                    write_log(PRIVKEY_LOG, '\n'.join(pk))
                finally:
                    log_lock.release()

        elif is_encrypted == 2: #encrypted
            log_lock.acquire()
            try:
                write_log(HASHES_LOG, wallet_path + '\n' + wallet_hash_to_brute)
            finally:
                log_lock.release()
    except Exception as exc:
        print(str(exc))

def thread_fun(dir, log_lock, HASHES_LOG, PRIVKEY_LOG):
    for path, subdirs, files in os.walk(dir):
        if len(files) == 0:
            continue
        for f in files:
            f_name, f_ext = op.splitext(f)
            if (f_ext!='.dat') or (f_name.find('wallet')==-1):
                continue
            try:
                fd=op.join(path, f)
                fd=op.normpath(fd)
                find_in_file(fd,log_lock,HASHES_LOG,PRIVKEY_LOG)
            except:
                print('ERROR:',sys.exc_info())
    return dir

def main():
    global SOURCE_DIR, LOG_DIR

    manager = mp.Manager()
    log_lock=manager.RLock()
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--threads', dest='threads', default=4, type=int, help="threads count, default 4")
    parser.add_argument('-s', '--sourcedir', dest='sourcedir', default=SOURCE_DIR, type=str, help="dir where logs with wallet.dat")
    parser.add_argument('-l', '--logdir', dest='logdir', default=LOG_DIR, type=str, help="dir where save worklogs: HASHES_LOG and PRIVKEY_LOG")
    args = parser.parse_args()

    SOURCE_DIR = args.sourcedir
    LOG_DIR = args.logdir
    THREADS_COUNT = args.threads
    n=datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    HASHES_LOG=f'hashes-{n}.txt'
    PRIVKEY_LOG=f'privkeys-{n}.txt'

    HASHES_LOG = op.join(LOG_DIR, HASHES_LOG)
    PRIVKEY_LOG = op.join(LOG_DIR, PRIVKEY_LOG)
    print(f"LOG_DIR: {LOG_DIR}")
    print(f"SOURCE_DIR: {SOURCE_DIR}")
    print(f"HASHES_LOG: {HASHES_LOG}")
    print(f"PRIVKEY_LOG: {PRIVKEY_LOG}")

    work_pool = mp.Pool(THREADS_COUNT)
    params=[(op.join(SOURCE_DIR,d),log_lock,HASHES_LOG,PRIVKEY_LOG) for d in os.listdir(SOURCE_DIR)]
    # print(params)
    res=work_pool.starmap(thread_fun, params)
    print('DONE.',len(res))
    print('\n'.join([str(r) for r in res]))




if __name__ == '__main__':
    main()
