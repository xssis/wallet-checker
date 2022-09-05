import sqlite3
import argparse
from datetime import datetime as dt

IN_FILE1='./f1.txt'
IN_FILE2='./f2.txt'

CREATE_TBL="CREATE TABLE tmp (addr VARCHAR(100) PRIMARY KEY NOT NULL UNIQUE ON CONFLICT IGNORE, amount VARCHAR(50))"
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('-t', default=10, type=int)
    parser.add_argument('-f1', default=IN_FILE1)
    parser.add_argument('-f2', default=IN_FILE2)
    args = parser.parse_args()

    IN_FILE1=args.f1
    IN_FILE2=args.f2

    con = sqlite3.connect("file::memory:?cache=shared", uri=True,detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute(CREATE_TBL)
    start_dt=dt.now()
    print('Start insert 1st file in tmp DB...')
    i=0
    with open(IN_FILE1,'r',encoding='utf-8') as f1:
        part=[]
        for line in f1:
            i+=1
            try:
                addr,amount=line.split()
                addr=addr.strip()
                amount=amount.strip()
            except:
                continue
            #amount=line.split(' ')[-1].strip()
            part.append((addr,amount))
            if len(part)==1000000:
                cur.executemany('INSERT into tmp values(?,?)',part)
                print(i)
                part=[]

        if len(part)>0:
            cur.executemany('INSERT into tmp values(?,?)',part)
    res=con.execute('select count(*) from tmp ').fetchone()[0]

    print('Insert %d DONE. '%res,dt.now()-start_dt)

    print('Check 2nd file...')
    i=0
    with open(IN_FILE2,'r',encoding='utf-8') as f2:
        for line in f2:
            addr=line.strip()
            res=con.execute('select * from tmp where addr=?',(addr,)).fetchone()
            if res is not None:
                print('\t'.join(res))
                i+=1
    print('Total found=',i)
    print('Time: ',dt.now()-start_dt)
    con.close()