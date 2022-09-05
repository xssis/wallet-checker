import datetime
import argparse
import multiprocessing as mp
from bip_utils import Bip44,Bip49,Bip84,WifDecoder,Bip44Coins
import sys

IN_FILE='address.txt'
OUT_FILE1='out_address.txt'
OUT_FILE2='out_wif_address.txt'
LOG_DIR='./'

def write_log(log_name,data):
    with open(LOG_DIR+log_name,'a',encoding='utf-8') as f:
        f.write(str(data)+'\n')

def thread_fun(wif_str,log_lock):
    try:
        wif = WifDecoder.Decode(wif_str)
        bbb44 = Bip44.FromAddressPrivKey(wif, Bip44Coins.BITCOIN)
        bbb49 = Bip49.FromAddressPrivKey(wif, Bip44Coins.BITCOIN)
        bbb84 = Bip84.FromAddressPrivKey(wif, Bip44Coins.BITCOIN)
        p2pkh=bbb44.PublicKey().ToAddress()
        p2sh=bbb49.PublicKey().ToAddress()
        p2wkh=bbb84.PublicKey().ToAddress()
        res1=f'{p2pkh}\n{p2sh}\n{p2wkh}'
        res2=f'{wif_str}\n{p2pkh}\n{p2sh}\n{p2wkh}\n'

        log_lock.acquire()
        try:
            write_log(OUT_FILE1, res1)
            write_log(OUT_FILE2, res2)
        finally:
            log_lock.release()
    except:
        print(sys.exc_info())

def main():
    manager = mp.Manager()
    log_lock=manager.RLock()
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', default=4, type=int)
    parser.add_argument('-f', default=IN_FILE)
    args = parser.parse_args()

    THREADS_COUNT=args.t
    in_file=args.f
    #n=datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    with open(OUT_FILE1,'w',encoding='utf-8') as f:
        pass
    with open(OUT_FILE2,'w',encoding='utf-8') as f:
        pass

    work_pool = mp.Pool(THREADS_COUNT)
    with open(in_file,'r',encoding='utf-8') as f:
        wifs=[]
        for line in f:
            wif=line.strip().split(':')[-1]
            wifs.append(wif)
            if len(wifs)==THREADS_COUNT*100:
                params=[(wif,log_lock) for wif in wifs]
                work_pool.starmap(thread_fun,params)
                wifs=[]

        if len(wifs)>0:
            params = [(wif, log_lock) for wif in wifs]
            work_pool.starmap(thread_fun, params)


if __name__ == '__main__':
    main()
