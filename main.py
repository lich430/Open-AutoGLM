from datetime import datetime
from buy_order import CoinOrder
import uiautomator2 as u2
import urllib.request
import json
import time
import os

from runner import AutoGLMRunner
import prompt

StabilityServiceUrl = "http://118.31.111.114:8080/stability_feed_v2.json"
LastCoinName = ""

def GetStabilityCoinNameRequest():
    with urllib.request.urlopen(StabilityServiceUrl) as response:
        json_text = response.read().decode('utf-8')
        coinList = json.loads(json_text)
        if len(coinList) > 0:
            TargetCoinName = coinList[0]
            return TargetCoinName
        return "NIGHT"

def PlayDealTask(orderClient: CoinOrder, llvmAgent: AutoGLMRunner):

    global LastCoinName

    if orderClient.IsFinish() and not orderClient.IsConfirm():
        UpdateTradeVolumeTask(orderClient,llvmAgent)
    if orderClient.IsFinish() and orderClient.IsConfirm():
        prompt.task_browse_square(llvmAgent)
        prompt.task_watch_live(llvmAgent)
        return

    coinName = GetStabilityCoinNameRequest()
    print(f"coinName: {coinName}")
    if coinName == "":
        prompt.task_browse_square(llvmAgent)
        return

    # 如果最新的代币和上次选择的的不一样，就需要重新进入交易页面, todo:或者直接在交易页面切换币种
    if LastCoinName != coinName:
        prompt.task_enter_alpha_trade(llvmAgent, coinName)
        prompt.task_reset_alpha_trade_page(llvmAgent)
        LastCoinName = coinName

    prompt.task_cancel_alpha_orders(llvmAgent)
    orderClient.BuyOrderAction(coinName)
    time.sleep(5)

def WalkPlazaTask(llvmAgent: AutoGLMRunner):
    prompt.task_browse_square(llvmAgent)

def UpdateTradeVolumeTask(orderClient: CoinOrder,llvmAgent: AutoGLMRunner):
    estimated_volume = prompt.task_get_alpha_estimated_volume(llvmAgent)
    print(f"获取预估的交易量: {estimated_volume}")
    if estimated_volume is None:
        return
    orderClient.Reset(estimated_volume)

def GetLLVMAgent() -> AutoGLMRunner:
    return AutoGLMRunner()

def main(serial:str, label:str, otp:str, money):
    # 设备配置
    today = datetime.now()
    print(f"{today} serial: {serial}, label:{label}, otp:{otp}, money:{money}")
    # 连接设备
    device = u2.connect(serial)
    orderClient = CoinOrder(device, label, otp, int(money))
    llvmAgent = GetLLVMAgent()

    WalkPlazaTask(llvmAgent)

    counter = 0
    while True:
        # 每交易4次查询一次交易量
        if counter >= 3:
            UpdateTradeVolumeTask(orderClient, llvmAgent)
            counter = 0

        counter = counter + 1

        # 进入交易页面
        PlayDealTask(orderClient, llvmAgent)
        time.sleep(2)

if __name__ == "__main__":
    main(os.environ["SERIAL"], "", "", 200)
