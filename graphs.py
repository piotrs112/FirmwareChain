from datetime import datetime

from matplotlib import pyplot as plt
from pymongo import MongoClient

col = MongoClient().bc_log.log

d = list(col.find({'msg': {'$in': ['I_AM_LEADER', 'GOT_NEW_BLOCK']}}))
t = [d["created"] for d in d]
d_t = 0


def replace(text):
    if text == "I_AM_LEADER":
        return "SEND"
    elif text == "GOT_NEW_BLOCK":
        return "GET"


for _d in d:
    _d['msg'] = replace(_d['msg'])

colors = ('b', 'g', 'r', 'c', 'm', 'y')

N_NODES = 5
BLOCKS = 10
TRANSACTIONS_PER_BLOCK = 1


def f(x): return x - d_t


d_t = min(t)


plt.rc('font', size=16)

for i in range(N_NODES):
    _t = t[i*5:(i+1)*5]
    _d = d[i*5:(i+1)*5]

    d_t = min(_t)
    plt.plot(list(map(f, _t)), [
             f"{d['msg']} #{i}" for d in _d], f'{colors[i]}o', label=f"Blok #{i}")
    plt.vlines(list(map(f, _t)), ymin=2*i, ymax=2*i+1, colors='grey')


#plt.title("Czas propagacji nowego bloku w sieci")
plt.grid()
plt.xlabel("Czas [s]")

plt.show()
