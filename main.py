from datetime import datetime
from buy_order import CoinOrder
import uiautomator2 as u2
import urllib.request
import json
import time
import os
from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
import prompt

StabilityServiceUrl = "http://118.31.111.114:8080/stability_feed_v2.json"


def GetStabilityCoinNameRequest():
    with urllib.request.urlopen(StabilityServiceUrl) as response:
        json_text = response.read().decode('utf-8')
        coinList = json.loads(json_text)
        if len(coinList) > 0:
            TargetCoinName = coinList[0]
            return TargetCoinName
        return ""

def PlayDealTask(orderClient: CoinOrder, llvmAgent: PhoneAgent):
    if not orderClient.IsFinish():
        coinName = GetStabilityCoinNameRequest()
        if coinName != "":
            # 调用LLVM跳转到交易页面
            result = prompt.task_enter_alpha_trade(llvmAgent, coinName)
            result = prompt.task_reset_alpha_trade_page(llvmAgent)
            while True:
                prompt.task_cancel_alpha_orders(llvmAgent)
                orderClient.BuyOrderAction(coinName)
                time.sleep(5)
                if orderClient.IsFinish():
                    return
                newCoinName = GetStabilityCoinNameRequest()
                # 去逛广场
                if newCoinName == "":
                    return
                # TODO::更换币种
                # if coinName != newCoinName:
                #     return
    else:
        # 调用LLVM跳转到交易额页面
        # TODO::
        pass

def WalkPlazaTask(llvmAgent: PhoneAgent):
    prompt.task_browse_square(llvmAgent)

def GetLLVMAgent() -> PhoneAgent:
    # Configure model
    model_config = ModelConfig(
        base_url="https://open.bigmodel.cn/api/coding/paas/v4",
        model_name="autoglm-phone",
        api_key="a8a74eb5e1f743579653310c73baa255.ACXboMXfiBpXUhEE",
    )

    # 创建 Agent
    agent = PhoneAgent(model_config=model_config)
    return agent

def main(serial:str, label:str, otp:str, money):
    # 设备配置
    today = datetime.now()
    print(f"{today} serial: {serial}, label:{label}, otp:{otp}, money:{money}")
    # 连接设备
    device = u2.connect(serial)
    orderClient = CoinOrder(device, label, otp, int(money))
    llvmAgent = GetLLVMAgent()

    while True:
        # 逛广场
        WalkPlazaTask(llvmAgent)

        # 进入交易页面
        PlayDealTask(orderClient, llvmAgent)
        time.sleep(2)
        # 返回手机的首页，防止占用手机时间
        # TODO::

if __name__ == "__main__":
    main(os.environ["SERIAL"], "", "", 10)
