import csv
import json
import redis


connection_pool = redis.ConnectionPool(host='localhost', port=6379)
connection = redis.Redis(connection_pool=connection_pool)


# def import_ips_to_redis(filename, conn=connection):
#     csv_file = csv.reader(open(filename, 'r'))
#     for count, row in enumerate(csv_file):
#         network = row[0] if row else ''
#         start_ip = network.partition("/")[0]
#
#         start_ip = int(ip_to_score(start_ip))
#         city_id = row[1] + "_" + str(count)
#         conn.zadd('ip2cityid:', city_id, start_ip)
#
#
# def import_cities_to_redis(filename, conn=connection):
#     for row in csv.reader(open(filename, 'r')):
#         if len(row) < 13 or not row[0].isdigit():
#             continue
#
#         city_id = row[0]
#         country = row[5]
#         continent = row[3]
#         city = row[10]
#         conn.hset('cityid2city:', city_id, json.dumps([city, country, continent]))


def ip_to_score(ip_address):
    score = 0
    for v in ip_address.split('.'):
        score = score * 256 + int(v, 10)
    return score


def find_city_by_ip(ip_address, conn=connection):

    if isinstance(ip_address, str):
        ip_address = ip_to_score(ip_address)
    city_id = conn.zrevrangebyscore('ip2cityid:', ip_address, 0, start=0, num=1)

    if not city_id:
        return None
    city_id = str(city_id[0]).partition('_')[0]
    city_id = city_id[2:]
    result = conn.hget('cityid2city:', city_id)

    return json.loads(result.decode('utf-8'))

