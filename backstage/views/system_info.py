#! /usr/bin/python3
# coding:utf-8

import sys
import os
import atexit
import time
import psutil


def get_cpu_state(interval=1):
    return str(psutil.cpu_percent(interval)) + "%"


def get_memory_state():
    memory_view = psutil.virtual_memory()
    memory_state = (
            memory_view.percent,
            str(int(memory_view.used/1024/1024))+"M",
            str(int(memory_view.total/1024/1024))+"M")
    return memory_state


def bytes2human(n):
    # """
    #         >>> bytes2human(10000)
    #         '9.8 K'
    #         >>> bytes2human(100001221)
    #         '95.4 M'
    # """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % n


def get_net_io_state():
    total_before = psutil.net_io_counters()
    time.sleep(1)
    total_after = psutil.net_io_counters()
    sent = total_after.bytes_sent - total_before.bytes_sent
    recv = total_after.bytes_recv - total_before.bytes_recv
    # print(sent, " | ", recv)
    return tuple([sent, recv])


def get_system_info():
    return {
        'cpu_state': get_cpu_state(),
        'memory_state_used': get_memory_state()[1],
        'memory_state_total': get_memory_state()[2],
        'memory_state_percentage': get_memory_state()[0],
        'sent_package': get_net_io_state()[0],
        'recv_package': get_net_io_state()[1],
        'upload_ratio': bytes2human(get_net_io_state()[0]),
        'download_ratio': bytes2human(get_net_io_state()[0])
    }


if __name__ == '__main__':
    print(get_cpu_state())
    print(get_memory_state())
    tot_before = psutil.net_io_counters()
    net = get_net_io_state()
    print(bytes2human(net[0]) + "/s")
    print(bytes2human(net[1]) + "/s")