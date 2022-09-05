# Чекер для массовой проверки всех приватных ключей из файлов wallet.dat

Все что я встречал в паблике или даже продаже тут у нас на форуме xss.is ищет в `wallet.dat` файлах слова `"name"` и выдергивает оттуда рядом лежащий адрес.
Но это в корне не правильно. Например, ваш стилер отработал в понедельник, то в `wallet.dat` будет только 1 строка с адресом записанном в адресной книге.
И если юзер в четверг решил перевести на этот wallet.dat биткоины то он нажмет в BitcoinCore кнопку `Create New Receiving Address` и в `wallet.dat` будет записан другой, новый адрес, о существовании которого паблик чекеры знать совсем не будут. 

А мой же скрипт выдергивает все приватные ключи из файла `wallet.dat` и потом второй дополнительный скрипт генерирует на основе найденных приватных кючей биткоин адреса всех трех типов для их удобной проверки на баланс.

## Суть работы

```bash
usage: wallet-parser-v2.py [-h] [-t THREADS] [-s SOURCEDIR] [-l LOGDIR]

  

optional arguments:

  -h, --help            show this help message and exit

  -t THREADS, --threads THREADS

                        количество потоков при запуске, по умолчанию 4

  -s SOURCEDIR, --sourcedir SOURCEDIR

                        директория, где расположены логи или файлы wallet.dat

  -l LOGDIR, --logdir LOGDIR

                        директория, куда запишутся логи работы скрипта: HASHES_LOG и PRIVKEY_LOG
```

Чтобы вытащить все адреса и привкеи из всех файлов `wallet.dat` нужно запустить `wallet-parser-v2.py`. Пример запуска:

`python3 wallet-parser-v2.py -t 4 --sourcedir '~/logs/' --logdir ~/work/`

На выходе в папке, указанной опцией `--logdir`, будут 2 файла:
 - hashes - для того что бы попытаться сбрутить (кто шарит тот поймет зачем)
 - privkeys - файл с адресами legacy типа и приватными ключами.

После того как скрипт `wallet-parser-v2.py` отработал, берем файл `privkeys` и переименовываем его в `address.txt`.

Далее запускаем скрипт `wif_to_address_v2.py`. Он нужен чтобы из всех приватных ключей, полученных из `wallet.dat` файлов вытащить адреса всех трех форматов. На выходе будет 2 файла:
 - `out_address.txt` - файл только с адресами (быстро чекнуть все адреса из этого файла можно с помощью скрипта `wallet_compare.py` из этой темы [link](https://xss.is/threads/51535/))
 - и для удобства `out_wif_address.txt` (если будет адрес с балансом просто вбиваем его в поиске по этому текстовику и быстро находим привкей от него).

## wallet_compare.py

Чекер написан на Python (для работы требуется версия 3.6 и выше)  
Поддерживает массовый чек следующих криптовалют Bitcoin, BitcoinCash, Bitcoin SV, Litecoin, Dash, Dogecoin  
  
Для запуска нужно перейти в папку с чекером в повершелле и выполнить  
`python3 wallet_compare.py -f1 файл_со_списком_адресов_с_балансами -f2 ваш_файл_с_любым_количеством_адресов. (каждый адрес с новой строки)`  

Так же для запуска нам понадобятся следующие файлы:

 - `blockchair_bitcoin_addresses_and_balance_LATEST.tsv` - все адреса с балансами Bitcoin
 - `blockchair_bitcoin-cash_addresses_latest.tsv `- все адреса с балансами BitcoinCash
 - `blockchair_bitcoin-sv_addresses_latest.tsv` - все адреса с балансами Bitcoin SV
 - `blockchair_dash_addresses_latest.tsv` - все адреса с балансами DASH
 - `blockchair_dogecoin_addresses_latest.tsv` - все адреса с балансами Dogecoin  
 - `blockchair_litecoin_addresses_latest.tsv` - все адреса с балансами Litecoin  
  
Лучше обновлять все эти файлы перед проверкой.  
  
Скачать актуальный первый файл можно отсюда на нормальной скорости: [List of all Bitcoin addresses with a balance](http://addresses.loyce.club/?C=M;O=D). Все остальные можно скачать [отсюда](https://gz.blockchair.com) (ограничение по скорости и максимум можно скачивать только 1 файл за раз)  

	Файлы по урлам обновляются 1-2 раза в день.  

Пример для биткоина (для других криптовалют аналогично только файл базы данных другой.

```bash
python3 wallet_compare.py -f1 blockchair_bitcoin_addresses_and_balance_LATEST.tsv -f2 файл_с_адресами_которые_хотите_чекнуть_на_баланс.txt
```

Скрипт для массового чека, можно скармливать файлы с десятками милн адресов и он их чекнет. Заботает в зависимости от железа, на i7 10875 отрабатывает за 25 сек 5 млн адресов.

# Установка:

Установить python3 версии не ниже 3.8 и менеджер пакетов pip3.

## Windows:

Найти и скачать пакет для установки `bsddb3-6.2.9-cp38-cp38-win32.whl`. Затем выполнить:

```bash
pip install bsddb3-6.2.9-cp38-cp38-win32.whl
```

## Ubuntu:
```bash
sudo apt-get install libdb++-dev
export BERKELEYDB_DIR=/usr
pip3 install bsddb3
```

## MacOS Catalina

```bash
brew install berkeley-db@4
BERKELEYDB_DIR=$(brew --prefix berkeley-db@4) pip3 install bsddb3
```

Для всех ОС после выполнения предыдущего шага:

```pip3 install -r requirements.txt```

