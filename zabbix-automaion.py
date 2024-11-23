import requests
import json
from datetime import datetime, timedelta
import math


zabbix_api_url = "http://x.x.x.x/api_jsonrpc.php"
api_key = "API TOKEN ZABBIX"


def get_graph_data(item_ids, time_from, time_till, limit=10):
    headers = {
        'Content-Type': 'application/json-rpc',
    }
    data = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": "3",
            "itemids": item_ids,
            "time_from": time_from,
            "time_till": time_till,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 36000
        },
        "auth": api_key,
        "id": 1
    }
    response = requests.post(zabbix_api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json().get('result')
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
def convert_timestamp_to_date(timestamp):
    dt_object = datetime.fromtimestamp(int(timestamp))
    return dt_object.strftime('%Y-%m-%d %H:%M:%S')


def get_time_range():
    end = datetime.now().replace(hour=00, minute=00, second=00)
    #end = datetime(2024, 9, 21, 0, 0, 0)
    start = end - timedelta(days=1)


    time_from = int(start.timestamp())
    time_till = int(end.timestamp())


    return time_from, time_till


def post_to_google_sheet_pribadi(data):
    url = "API APPS SCRIPT"
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Data berhasil dikirim ke spreadsheet pribadi")
    else:
        print(f"Error saat mengirim data: {response.status_code} - {response.text}")


if __name__ == "__main__":
    item_id_rx = "57971"
    item_id_tx = "57927"
    graph_name = "Localloop"


    time_from, time_till = get_time_range()


    graph_data = get_graph_data([item_id_rx, item_id_tx], time_from, time_till)


    if graph_data:
        data_by_itemid = {}
        for data_point in graph_data:
            item_id = data_point['itemid']
            value = float(data_point['value']) * 0.001


            if item_id not in data_by_itemid:
                data_by_itemid[item_id] = []
            data_by_itemid[item_id].append(value)


        def process_graph_data(data, label):
            total_value = sum(data)
            count = len(data)
            max_value = max(data) if count > 0 else 0
            average_value = total_value / count if count > 0 else 0


            total_value = round(total_value, 2)
            max_value = round(max_value, 2)
            average_value = round(average_value, 2)


            return total_value, average_value, max_value


        if math.isnan(value):
            value = 0


        if item_id not in data_by_itemid:
            data_by_itemid[item_id] = []
        data_by_itemid[item_id].append(value)




        if item_id_rx in data_by_itemid:
            total_rx, average_rx, max_rx = process_graph_data(data_by_itemid[item_id_rx], "received")
            start_time = convert_timestamp_to_date(time_from)
            end_time = convert_timestamp_to_date(time_till)
            print(f"{graph_name}, start: {start_time}, end: {end_time}, average value_rx: {average_rx:.2f}, max_rx: {max_rx:.2f}")
        else:
            print("Tidak ada data untuk grafik received.")


        if item_id_tx in data_by_itemid:
            total_tx, average_tx, max_tx = process_graph_data(data_by_itemid[item_id_tx], "send")
            start_time = convert_timestamp_to_date(time_from)
            end_time = convert_timestamp_to_date(time_till)
            print(f"{graph_name}, start: {start_time}, end: {end_time}, average value_tx: {average_tx:.2f}, max_tx: {max_tx:.2f}")
        else:
            print("Tidak ada data untuk grafik send.")


        post_data = {
            "name": graph_name,
            "start_time": start_time,
            "end_time": end_time,
            "avg_rx": average_rx,
            "max_rx": max_rx,
            "avg_tx": average_tx,
            "max_tx": max_tx
        }


        post_to_google_sheet_pribadi(post_data)


    else:
        print("Tidak ada data yang ditemukan.")

