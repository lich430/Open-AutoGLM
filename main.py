from datetime import datetime
import uiautomator2 as u2
import urllib.request
import json
import time
import random

import buy_order
from runner import AutoGLMRunner
import prompt
from hyper_glm_trade import ClientLogWriter, DeviceOps, GLMVisionClient, HyperTradeBot, get_api_key_from_env

StabilityServiceUrl = "http://118.31.111.114:8080/stability_feed_v2.json"
LastCoinName = ""
CounterOfCoinRequest = 0
MaxRequest = 3

def GetStabilityCoinNameRequest():
    with urllib.request.urlopen(StabilityServiceUrl) as response:
        json_text = response.read().decode('utf-8')
        coinList = json.loads(json_text)
        if len(coinList) > 0:
            return coinList[0]
        return ""

def PlayDealTask(bot: HyperTradeBot, llvmAgent: AutoGLMRunner):

    global LastCoinName
    global CounterOfCoinRequest

    def do_task():
        # 随机选择广场，还是任务
        index = random.randint(0, 9)
        taskName = "square"
        if index > 5:
            # 任务
            taskName = bot.TakeTask()
            # 不在乎结果，可以先记录状态
            bot.SaveTaskResult(taskName, True)
        ClientLogWriter(f"随机选择事件: {taskName}")
        if taskName == "bnb":
            prompt.task_spot_buy_bnb(llvmAgent)
        elif taskName == "futures":
            pass
        elif taskName == "finance":
            pass
        elif taskName == "square" or taskName == "":
            prompt.task_browse_square(llvmAgent)

    if bot.IsFinish() and not bot.IsConfirm():
        UpdateTradeVolumeTask(bot,llvmAgent)
    if bot.IsFinish() and bot.IsConfirm():
        prompt.task_browse_square(llvmAgent)
        prompt.task_watch_live(llvmAgent)
        return

    coinName = GetStabilityCoinNameRequest()
    print(f"coinName: {coinName}")
    if coinName == "":
        CounterOfCoinRequest += 1
        buy_order.ClientLogWriter("没有获取到稳定币")
        # 空闲时间
        if CounterOfCoinRequest < MaxRequest:
             do_task()
             return
        if CounterOfCoinRequest >= MaxRequest:
            CounterOfCoinRequest = 0
            coinName = bot.GetDefaultCoin()
        # 没有稳定币，进入空闲时间
        if coinName == "":
            do_task()
            return

    # 如果最新的代币和上次选择的的不一样，就需要重新进入交易页面, todo:或者直接在交易页面切换币种
    if LastCoinName != coinName:
        prompt.task_enter_alpha_trade(llvmAgent, coinName)
        #prompt.task_reset_alpha_trade_page(llvmAgent)
        LastCoinName = coinName

    # prompt.task_cancel_alpha_orders(llvmAgent)

    result = bot.alpha_trade(coinName, buy_ratio=0.95, buy_markup=1.03, sell_discount=0.97)
    print("DONE:", result)
    time.sleep(5)

def WalkPlazaTask(llvmAgent: AutoGLMRunner):
    prompt.task_browse_square(llvmAgent)

def UpdateTradeVolumeTask(bot: HyperTradeBot,llvmAgent: AutoGLMRunner):
    estimated_volume = prompt.task_get_alpha_estimated_volume(llvmAgent)
    buy_order.ClientLogWriter(f"获取预估的交易量: {estimated_volume}")
    if type(estimated_volume) is tuple:
        return bot.Reset(estimated_volume[0])
    if type(estimated_volume) is float:
        bot.Reset(estimated_volume)

def GetLLVMAgent() -> AutoGLMRunner:
    return AutoGLMRunner()

def main(serial:str, label:str, otp:str, money:float):
    # 设备配置
    today = datetime.now()
    print(f"{today} serial: {serial}, label:{label}, otp:{otp}, money:{money}")
    # 连接设备
    llvmAgent = GetLLVMAgent()
    device_factory = llvmAgent.get_device_factory()
    devices = device_factory.list_devices()
    if not devices:
        raise RuntimeError("No devices detected")

    device_id = devices[0].device_id
    if device_id != serial:
        ClientLogWriter("手机不识别")
        time.sleep(90)
        return

    # api_key = get_api_key_from_env("BIGMODEL_API_KEY")  # 推荐用环境变量
    api_key = "d02cf9e65048471d92c4fd840a280934.OCIg95VIrqTnKboe"
    glm = GLMVisionClient(api_key=api_key, model="glm-4.6v")

    dev = DeviceOps(device_factory, device_id)
    bot = HyperTradeBot(device_id, label, money, glm, dev)

    #WalkPlazaTask(llvmAgent)

    counter = 0
    while True:
        # 每交易4次查询一次交易量
        if counter >= 3:
            UpdateTradeVolumeTask(bot, llvmAgent)
            counter = 0

        counter = counter + 1

        # 进入交易页面
        PlayDealTask(bot, llvmAgent)
        time.sleep(2)

if __name__ == "__main__":
    main("", "KOGE|1", "", 100)
