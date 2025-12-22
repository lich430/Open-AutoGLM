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

PromptPageReady = "当前页面是alpah交易的页面  1：如果发现选中的是即时的交易模式，就切换为限价的模式。2：如果发现在页面上用户的行为是卖出，就切换为买入。3：向下滑动页面，如果发现有未完成的委托单就取消所有的单 子，取消完成后向上滑动页面到顶部"
PromptButtons = ""

def ClientLogWriter(text, end="\n"):
    print("INFO::", time.asctime(), text)

class TaskCounter:
    """
    轻量级本地文件缓存计数器，支持按日期自动归零。
    用法：
        counter = TaskCounter(secret="abc123")
        data = counter.load()          # 读缓存 / 返回默认
        data["counter"] += 1
        counter.save(data)             # 写回磁盘
    或者链式：
        counter.inc("counter", 1)      # 直接 +1 并落盘
    """
    DEFAULT_FORMAT = "%Y-%m-%d"          # 按天刷新，可改成 "%Y-%m" 等
    DEFAULT_CACHE_DIR  = Path("cache")
    DEFAULT_FILENAME_TPL = "task_counter_{secret}.json"

    def __init__(
        self,
        secret: str,
        *,
        cache_dir: Union[str, Path] = DEFAULT_CACHE_DIR,
        filename_tpl: str = DEFAULT_FILENAME_TPL,
        date_format: str = DEFAULT_FORMAT,
        default_fields: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.secret = secret
        self.cache_dir  = Path(cache_dir)
        self.file_path  = self.cache_dir / filename_tpl.format(secret=secret)
        self.date_format = date_format
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # 默认数据结构
        self._default: Dict[str, Any] = default_fields or {
            "date": self._date_key(),
            "counter": 0,
            "cash": 0,
        }

    # -------------------- 公有 API --------------------
    def load(self) -> Dict[str, Any]:
        """加载缓存，若文件/日期失效则返回默认结构。"""
        if not self.file_path.exists():
            self.logger.info("缓存文件不存在，使用默认值")
            return self._default.copy()

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, IOError) as exc:
            self.logger.warning("缓存文件损坏: %s，使用默认值", exc)
            return self._default.copy()

        # 日期维度校验
        if not self._is_same_period(raw.get("date")):
            self.logger.info("日期维度已变化，重置计数器")
            return self._default.copy()

        # 把 date 转回 datetime 对象，方便外部使用
        raw["date"] = datetime.fromtimestamp(raw["date"], tz=timezone.utc)
        return raw

    def save(self, data: Dict[str, Any]) -> None:
        """将数据落盘；date 字段会被自动转成 timestamp。"""
        if not isinstance(data, dict):
            raise TypeError("data 必须是 dict")

        # 深拷贝，防止外部修改继续污染
        to_save = data.copy()
        to_save["date"] = self._normalize_date(to_save.get("date")).timestamp()

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
        self.logger.debug("计数器已保存 -> %s", self.file_path)

    def inc(self, key: str, delta: float|int = 1) -> Dict[str, Any]:
        """原子 +delta 并落盘，返回最新数据。"""
        data = self.load()
        data[key] = data.get(key, 0) + delta
        self.save(data)
        return data

    # --------------- 快捷“安全”版本 ---------------
    def safe_load(self) -> Dict[str, Any]:
        try:
            return self.load()
        except Exception:
            self.logger.exception("加载失败，返回默认")
            return self._default.copy()

    def safe_save(self, data: Dict[str, Any]) -> bool:
        try:
            self.save(data)
            return True
        except Exception:
            self.logger.exception("保存失败")
            return False

    # -------------------- 内部工具 --------------------
    def _date_key(self) -> datetime:
        """返回当前日期维度对应的 datetime（UTC 00:00）。"""
        now = datetime.now(tz=timezone.utc)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    def _normalize_date(self, value) -> datetime:
        """把外部传入的 date 字段统一成 datetime。"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        raise TypeError(f"不支持的 date 类型: {type(value)}")

    def _is_same_period(self, date_value) -> bool:
        """
        按 date_format 维度比较日期是否相同。
        例如 format=%Y-%m-%d 则比较到天；%Y-%m 则比较到月。
        """
        if not date_value:
            return False
        try:
            history = datetime.fromtimestamp(date_value, tz=timezone.utc)
        except (TypeError, OSError):
            return False
        return history.strftime(self.date_format) == self._date_key().strftime(self.date_format)

class OrderPageButton:
    def __init__(self, pricePoint:tuple[float|int, float|int], sellPricePoint:tuple[float|int, float|int], volumePoint:tuple[float|int, float|int], actionButton:tuple[float|int, float|int]):
        self.volumePoint = volumePoint
        self.actionButton = actionButton
        self.pricePoint = pricePoint
        self.sellPricePoint = sellPricePoint

class CoinOrder:
    def __init__(self, device: u2.Device, label:str, otp:str, money:float|int):
        self.device = device
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
            self.coinName = label.strip("|4")

    def GetDefaultCoin(self):
        return self.coinName

    def GetOrderPageButton(self):
        # 获取当前界面的层级结构
        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        pricePoint = self.GetElemPointByAttribute(root, "text", "价格")
        print("购买价格坐标:", pricePoint)
        # 去掉输入框内数据
        self.Click(pricePoint)
        self.Sleep(1)
        self.ClearText(pricePoint)
        self.Sleep(1)

        xml = self.device.dump_hierarchy()
        root = ET.fromstring(xml)
        volumePoint = self.GetElemPointByAttribute(root, "text", "总额(USDT)")
        print("总额坐标:", volumePoint)
        actionButton = self.GetElemPointByAttribute(root, "text", "买入 *")
        print("购买坐标:", actionButton)
        sellPricePoint = self.GetElemPointByAttribute(root, "text", "卖出价格 (USDT)")
        print("卖出价格坐标:", sellPricePoint)
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

        if not hasattr(self, "orderPageButton"):
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
        # 全选
        self.device.press(123)
        # 删除
        for x in range(20):
            self.device.press(67)
        # 输入
        self.Sleep(1)
        self.device.send_keys(str(text))


    def ClearText(self, points:tuple[float|int, float|int]):
        # 向当前焦点所在的输入框发送数字
        self.Click(points)
        self.Sleep(0.3)
        # 全选
        self.device.press(123)
        # 删除
        for x in range(20):
            self.device.press(67)
