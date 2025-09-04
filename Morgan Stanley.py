import json
import requests
import time
URL = "http://fx-trading-game-york.westeurope.azurecontainer.io:443"

def get_positions(trader_id, currency):
    api_url=URL+ "/positions/XMEENUrrsLjR3U54WEI547YQ1ulT4p7L"
    res=requests.get(api_url)
    if res.status_code==200:
        return json.loads(res.content.decode('utf-8'))[currency]
    return None

start_trade = 0
total_time = 0
total_price = 0
TRADER_ID = "XMEENUrrsLjR3U54WEI547YQ1ulT4p7L"
GBP = get_positions(TRADER_ID, "GBP")
EUR = get_positions(TRADER_ID, "EUR")
quantity = 0

period = 1
baseline_avg = 0
baseline_avg_total = 0
sell_avg = 0
sell_count = 0
sell_avg_total = 0
buy_avg = 0
buy_count = 0
buy_avg_total = 0

class Side:
    BUY = "buy"
    SELL = "sell"


def get_price():
    api_url = URL + "/price/EURGBP"
    res = requests.get(api_url)
    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))["price"]
    return None

def trade(trader_id, qty, side):
    api_url = URL + "/trade/EURGBP"
    data = {"trader_id": trader_id, "quantity": qty, "side": side}
    res = requests.post(api_url, json=data)
    if res.status_code == 200:
        resp_json = json.loads(res.content.decode('utf-8'))
        if resp_json["success"]:
            return resp_json["price"]
    return None

if __name__ == '__main__':
    print("Expected to trade at:" + str(get_price()))
    print("Effectively traded at:" + trade(TRADER_ID, 100, Side.BUY))
    while True:
        time.sleep(1)
        total_time += 1
        current_price = get_price()
        GBP = get_positions(TRADER_ID, "GBP")
        EUR = get_positions(TRADER_ID, "EUR")

        #AVG CALC
        baseline_avg_total += current_price
        baseline_avg = baseline_avg_total/total_time
        if current_price < baseline_avg:
            sell_count += 1
            sell_avg_total += current_price
            sell_avg = sell_avg_total/sell_count
        elif current_price > baseline_avg:
            buy_count += 1
            buy_avg_total += current_price
            buy_avg = buy_avg_total/buy_count

        #Switch period and reset time
        if total_time == 1200 and period == 1:
            period = 2
            total_time = 0
            baseline_avg, baseline_avg_total = 0
            sell_avg, sell_count, sell_avg_total = 0
            buy_avg, buy_count, buy_avg_total = 0
        elif total_time == 1200 and period == 2:
            period = 3
            total_time = 0
            baseline_avg, baseline_avg_total = 0
            sell_avg, sell_count, sell_avg_total = 0
            buy_avg, buy_count, buy_avg_total = 0
        elif total_time == 1080 and period == 3:
            period = 4

        #TRADE
        if period == 1:
            if 300 <= total_time < 1200: #waits 5 mins before trading
                if sell_avg < current_price < baseline_avg:
                    trade(TRADER_ID, 100000 * ((baseline_avg - current_price)/(baseline_avg - sell_avg)), "sell")
                elif current_price < sell_avg:
                    trade(TRADER_ID, 100000, "sell")
        elif period == 2:
            if 120 < total_time < 1200: #wait 2 mins before trading
                if buy_avg > current_price > baseline_avg:
                    trade(TRADER_ID, 100000 * ((buy_avg - current_price)/(buy_avg - baseline_avg)), "buy")
                elif current_price > buy_avg:
                    trade(TRADER_ID, 100000, "buy")
        elif period == 3:
            if 120 < total_time < 1080:  # wait 2 mins before trading and stop 2 mins early
                if buy_avg > current_price > baseline_avg:
                    trade(TRADER_ID, 100000 * ((buy_avg - current_price)/(buy_avg - baseline_avg)), "buy")
                elif current_price > buy_avg:
                    trade(TRADER_ID, 100000, "buy")
                elif sell_avg < current_price < baseline_avg:
                    trade(TRADER_ID, 100000 * ((baseline_avg - current_price)/(baseline_avg - sell_avg)), "sell")
                elif current_price < sell_avg:
                    trade(TRADER_ID, 100000, "sell")
        elif period == 4:
            total_amount_GBP = GBP + (EUR * current_price)
            trade(TRADER_ID, total_amount_GBP*0.3, "buy")