#사용자가 보유하고 있는 코인에 한합니다.


wanna_sell_coin = input("대문자로 판매를 원하는 원화코인을 적어주세요:")
wanna_sell_coin_benefit = float(input("익절을 원하는 코인가격을 알려주세요:"))
wanna_sell_coin_sonjul = float(input("손절을 원하는 코인가격을 알려주세요:"))

for b in balance():
    if b['currency'] == wanna_sell_coin:
        sell_volume = b['balance']
wanna_sell_coin = "KRW-"+wanna_sell_coin
while True:
    time.sleep(1)
    print(coin_price(wanna_sell_coin))    
    try:
        if coin_price(wanna_sell_coin)>wanna_sell_coin_benefit:
            print("익절을 진행합니다.")
            sell_market(wanna_sell_coin,sell_volume)
            break
        elif coin_price(wanna_sell_coin)<wanna_sell_coin_sonjul:
            print("손절을 진행합니다.")
            sell_market(wanna_sell_coin,sell_volume)
            break
    except:
        print("오류발생")

balance()
