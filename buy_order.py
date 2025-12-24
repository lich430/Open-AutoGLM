import os
import time
from datetime import datetime, timezone
from typing import List, Tuple,Dict, Any, Optional, Union
import uiautomator2 as u2
import random
import select
from xml.etree import ElementTree as ET
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from task_counter import TaskCounter
from phone_agent.agent import PhoneAgent
from phone_agent.device_factory import DeviceFactory

PromptPageReady = "当前页面是alpah交易的页面  1：如果发现选中的是即时的交易模式，就切换为限价的模式。2：如果发现在页面上用户的行为是卖出，就切换为买入。3：向下滑动页面，如果发现有未完成的委托单就取消所有的单 子，取消完成后向上滑动页面到顶部"
PromptButtons = ""

def ClientLogWriter(text, end="\n"):
    print("INFO::", time.asctime(), text)

class OrderPageButton:
    def __init__(self, pricePoint:tuple[float|int, float|int], sellPricePoint:tuple[float|int, float|int], volumePoint:tuple[float|int, float|int], actionButton:tuple[float|int, float|int]):
        self.volumePoint = volumePoint
        self.actionButton = actionButton
        self.pricePoint = pricePoint
        self.sellPricePoint = sellPricePoint

class CoinOrder:
    def __init__(self, device: u2.Device, deviceFactory: DeviceFactory, deviceId: str, label:str, otp:str, money:float|int):
        self.device = device
        self.deviceFactory = deviceFactory
        self.deviceId = deviceId
        self.label = label
        self.otp = otp
        self.money = money
        self.isFourTimes = False
        self.coinName = ""
        self.totalDeal = 0
        self.screen_width, self.screen_height = self.device.window_size()
        self.serial = device._serial
        self.taskCounter = TaskCounter(self.serial)
        if label != "":
            ClientLogWriter("用户指定稳定币:" + label)
            if label.endswith("|4"):
                self.isFourTimes = True
            self.coinName = label.strip("|4").strip("|1")

    def GetDefaultCoin(self):
        return self.coinName

    def GetOrderPageButton(self):
        # 获取当前界面的层级结构
        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        pricePoint = self.GetElemPointByAttribute(root, "text", "价格")
        ClientLogWriter(f"购买价格坐标: {pricePoint}")
        # 去掉输入框内数据
        self.Click(pricePoint)
        self.Sleep(1)
        self.ClearText(pricePoint)
        self.Sleep(1)

        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        volumePoint = self.GetElemPointByAttribute(root, "text", "总额(USDT)")
        ClientLogWriter(f"总额坐标: {volumePoint}")
        actionButton = self.GetElemPointByAttribute(root, "text", "买入 *")
        ClientLogWriter(f"购买坐标: {actionButton}")
        sellPricePoint = self.GetElemPointByAttribute(root, "text", "卖出价格 (USDT)")
        ClientLogWriter(f"卖出价格坐标: {sellPricePoint}")
        self.orderPageButton = OrderPageButton(pricePoint, sellPricePoint, volumePoint, actionButton)

    def Sleep(self, seconds: float | int):
        seconds = seconds + random.randint(0, 1000) * 0.001

        # 判断操作系统，Windows 使用 time.sleep，其他系统使用 select.select
        if os.name == 'nt':  # Windows 系统
            time.sleep(seconds)
        else:  # 非 Windows 系统（Linux, macOS 等）
            select.select([], [], [], seconds)

    def ShortRollUp(self):
        screen_width, screen_height = self.device.window_size()

        # 定义起始坐标和结束坐标
        start_x = screen_width // 2  # 屏幕中间的 x 坐标
        start_y = screen_height * 0.8  # 屏幕底部 80% 的 y 坐标
        end_x = screen_width // 2  # 屏幕中间的 x 坐标
        end_y = screen_height * 0.6  # 屏幕顶部 20% 的 y 坐标

        self.device.swipe(start_x, start_y, end_x, end_y, duration=0.5)

    def QuickRollDown(self):
        screen_width, screen_height = self.device.window_size()

        # 定义起始坐标和结束坐标
        start_x = screen_width // 2  # 屏幕中间的 x 坐标
        start_y = screen_height * 0.2  # 屏幕底部 80% 的 y 坐标
        end_x = screen_width // 2  # 屏幕中间的 x 坐标
        end_y = screen_height * 0.3  # 屏幕顶部 20% 的 y 坐标

        # 执行下滑动作
        self.device.swipe(start_x, start_y, end_x, end_y, duration=0.01)

    def GetOfferPriceAndPoint(self, root) -> float:
        # 获取当前界面的层级结构
        resId = "com.binance.dev:id/price"

        # 遍历所有元素
        for elem in root.iter():
            resourceId = elem.get("resource-id")
            text = elem.get('text')
            if resourceId and resourceId.strip() == resId:
                if text is not None:
                    return float(text.strip('$'))
        # 没有找到最新价格
        return 0

    def Bounds2Point(self, bounds):
        # 使用 bounds 信息
        bounds = bounds.strip('[').strip(']').split('][')
        # print(bounds)
        x1, y1 = map(int, bounds[0].split(','))
        x2, y2 = map(int, bounds[1].split(','))
        x = random.randint(x1 - 1, x2 - 1) + random.randint(0, 999) * 0.001
        y = random.randint(y1 - 1, y2 - 1) + random.randint(0, 999) * 0.001
        return (x, y)

    def GetElemPointByAttribute(self, root, attribute, value):
        # 遍历所有元素
        pattern = False
        if value.endswith("*"):
            value = value.strip("*")
            pattern = True

        for elem in root.iter():
            v = elem.get(attribute)
            if pattern:
                if v and v.startswith(value):
                    # 获取元素的资源ID或描述
                    bounds = elem.get('bounds')
                    # bounds是OS系统提供，无法缺失
                    # 使用bounds定位元素
                    if bounds:
                        return self.Bounds2Point(bounds)
            elif v and v.strip() == value:
                # 获取元素的资源ID或描述
                bounds = elem.get('bounds')
                # bounds是OS系统提供，无法缺失
                # 使用bounds定位元素
                if bounds:
                    return self.Bounds2Point(bounds)
        return (0, 0)

    def Click(self, point:Tuple[float, float]):
        self.device.click(*point)

    def GetTotalMoneyByXml(self, root)-> float:
        parent = False
        text = "可用"
        money = 0.0

        # 遍历所有元素
        for elem in root.iter():
            txt = elem.get('text')
            if parent is False and txt == text:
                parent = True
                continue
            if parent and txt.endswith(" USDT"):
                fields = txt.strip().split(" ")
                if len(fields) > 1:
                    m = fields[0]
                    print("可用总资金: ", m)
                    m = m.replace(",", "")
                    money = int(float(m) * 0.9)
                    break
        return money

    def Run(self):
        pass

    def IsFinish(self) -> bool:
        cachedData = self.taskCounter.load()
        result = (cachedData["cash"] >= self.money)
        if result:
            ClientLogWriter("IsFinish() ==> 完成")
        return result

    def IsConfirm(self) -> bool:
        cachedData = self.taskCounter.load()
        checked = cachedData.get("checked")
        if checked is None:
            return False
        return checked

    def Reset(self, cash: float):
        cachedData = self.taskCounter.load()
        cachedData["cash"] = cash
        if cash >=self.money:
            cachedData["checked"] = True
        self.taskCounter.save(cachedData)

    def BuyOrderAction(self, coinName:str):
        # 快速下拉
        self.QuickRollDown()
        self.Sleep(1)

        # 获取坐标
        self.GetOrderPageButton()

        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        latestPrice = self.GetOfferPriceAndPoint(root)
        print("找到最新价格: %s" % latestPrice)

        money = self.GetTotalMoneyByXml(root)
        if money == "0":
            ClientLogWriter("没有足够的资金")
            return False
        ClientLogWriter("可用总资金: %s" % money)

        # 计算价格
        buyPrice, sellPrice = self.MakeNewPricePair(latestPrice)
        print("最新价格: %s, 买入价格: %s， 卖出价格: %s" % (latestPrice, buyPrice, sellPrice))

        ClientLogWriter("输入买入价格: %s" % buyPrice)
        self.InputText(self.orderPageButton.pricePoint, buyPrice)

        ClientLogWriter("输入购买总金额: %s" % money)
        self.InputText(self.orderPageButton.volumePoint, money)
        ClientLogWriter("输入卖出价格: %s" % sellPrice)
        self.InputText(self.orderPageButton.sellPricePoint, sellPrice)

        # 触发交易
        self.Click(self.orderPageButton.actionButton)
        self.Sleep(3)

        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        point = self.GetElemPointByAttribute(root, "text", "确认")
        if len(point) == 0:
            print("买单 确认 未完成")
            return False
        self.Click(point)

        if (coinName == self.coinName) and (not self.isFourTimes):
            self.totalDeal += money
        else:
            self.totalDeal += money*4
            self.taskCounter.inc("cash", money*4)
        print("买单 确认 完成")
        return True

    def MakeNewPricePair(self, price):
        price_ = float(price)
        return price_ * 1.04, price_ * 0.96

    def InputText(self, points:tuple[float|int, float|int], price:float):
        text = str(price)
        # 向当前焦点所在的输入框发送数字
        self.Click(points)
        self.Sleep(0.3)
        self.deviceFactory.clear_text(self.deviceId)
        # # 输入
        self.Sleep(1)
        self.deviceFactory.type_text(str(text), self.deviceId)


    def ClearText(self, points:tuple[float|int, float|int]):
        # 向当前焦点所在的输入框发送数字
        self.Click(points)
        self.Sleep(0.3)
        self.deviceFactory.clear_text(self.deviceId)
