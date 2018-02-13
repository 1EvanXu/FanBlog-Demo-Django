import time
import threadpool


def sayhello(str, t):
    print("Hello ", str, "-", t)
    time.sleep(2)


if __name__ == '__main__':
    name_list = [(None, {'str':"a", "t": "a"})]
    start_time = time.time()
    pool = threadpool.ThreadPool(10)
    requests = threadpool.makeRequests(sayhello, name_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    print('%d second' % (time.time() - start_time))