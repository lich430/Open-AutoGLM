# hyper_glm_trade.py
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from task_counter import TaskCounter

import requests


# ----------------------------
# 1) 解析：页面六要素（4个点 + USDT + 币价）
# ----------------------------
@dataclass(frozen=True)
class TradeTargets:
    price_input_center: Tuple[int, int]
    total_usdt_input_center: Tuple[int, int]
    sell_price_input_center: Tuple[int, int]
    buy_button_center: Tuple[int, int]
    available_usdt: float
    coin_price_usd: float


def parse_trade_targets(resp_text: str) -> Optional[TradeTargets]:
    """
    从 GLM 完整 JSON 响应（response.text）中解析出：
      - 4个坐标 (x,y)
      - available_usdt
      - coin_price_usd
    要求 content 形如：
      hyper(180,345),(180,490),(180,625),(x4,y4),26.97 USDT,$0.016087byte
    """
    try:
        obj = json.loads(resp_text)
        content = obj["choices"][0]["message"]["content"]
    except Exception:
        return None

    if not isinstance(content, str):
        return None

    content = content.strip()

    coords = re.findall(r"\((\d+)\s*,\s*(\d+)\)", content)
    if len(coords) < 4:
        return None

    c1 = (int(coords[0][0]), int(coords[0][1]))
    c2 = (int(coords[1][0]), int(coords[1][1]))
    c3 = (int(coords[2][0]), int(coords[2][1]))
    c4 = (int(coords[3][0]), int(coords[3][1]))

    m_avail = re.search(r",\s*([0-9]+(?:\.[0-9]+)?)\s*USDT\s*,", content, flags=re.IGNORECASE)
    if not m_avail:
        return None
    available_usdt = float(m_avail.group(1))

    m_price = re.search(r",\s*\$\s*([0-9]+(?:\.[0-9]+)?)\s*byte\s*$", content, flags=re.IGNORECASE)
    if not m_price:
        return None
    coin_price_usd = float(m_price.group(1))

    return TradeTargets(
        price_input_center=c1,
        total_usdt_input_center=c2,
        sell_price_input_center=c3,
        buy_button_center=c4,
        available_usdt=available_usdt,
        coin_price_usd=coin_price_usd,
    )


# ----------------------------
# 2) 解析：弹窗确认按钮坐标 [[x,y]] / [x,y] / 任意文本数字
# ----------------------------
def extract_confirm_button_xy(resp_text: str) -> Optional[Tuple[int, int]]:
    try:
        obj = json.loads(resp_text)
        content = obj["choices"][0]["message"]["content"]
    except Exception:
        return None

    if not isinstance(content, str):
        return None

    content = content.strip()

    # 优先把 content 当 JSON 数组解析（[[x,y]] 或 [x,y]）
    for candidate in (content, content.lstrip("\ufeff")):
        try:
            val = json.loads(candidate)

            # [[x,y]]
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], list) and len(val[0]) >= 2:
                x, y = val[0][0], val[0][1]
                return int(round(float(x))), int(round(float(y)))

            # [x,y]
            if isinstance(val, list) and len(val) >= 2 and not isinstance(val[0], list):
                x, y = val[0], val[1]
                return int(round(float(x))), int(round(float(y)))
        except Exception:
            pass

    # 兜底：抓前两个数字
    nums = re.findall(r"-?\d+(?:\.\d+)?", content)
    if len(nums) >= 2:
        return int(round(float(nums[0]))), int(round(float(nums[1])))

    return None


# ----------------------------
# 3) GLM 调用封装（图文消息）
# ----------------------------
class GLMVisionClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        model: str = "glm-4.6v",
        timeout_s: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout_s = timeout_s

    def chat_image_text(self, image_base64_url: str, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_base64_url}},
                        {"type": "text", "text": text},
                    ],
                }
            ],
            "stream": False,
            "thinking": {"type": "enabled", "clear_thinking": True},
            "do_sample": True,
            "temperature": 1,
            "top_p": 0.95,
            "tool_stream": False,
            "response_format": {"type": "text"},
        }

        r = requests.post(self.base_url, json=payload, headers=headers, timeout=self.timeout_s)
        r.raise_for_status()
        return r.text


# ----------------------------
# 4) 设备操作封装（把全局变量去掉）
# ----------------------------
class DeviceOps:
    def __init__(self, device_factory, device_id: str):
        self.device_factory = device_factory
        self.device_id = device_id

    def screenshot(self):
        return self.device_factory.get_screenshot(self.device_id)

    def tap_rel_1000(self, x_rel: float, y_rel: float, screen_w: int, screen_h: int):
        """把 0~1000 的相对坐标转换为像素点击（你原来的 tap 做的就是这个）"""
        x = int(x_rel / 1000 * screen_w)
        y = int(y_rel / 1000 * screen_h)
        self.device_factory.tap(x, y, self.device_id)

    def clear_and_type(self, text: str):
        self.device_factory.clear_text(self.device_id)
        self.device_factory.type_text(text, self.device_id)


# ----------------------------
# 5) 一键流程封装：识别->输入->买入->弹窗确认
# ----------------------------
class HyperTradeBot:
    def __init__(self, serial: str, label: str, money:float, glm: GLMVisionClient, dev: DeviceOps):
        self.glm = glm
        self.dev = dev
        self.money = money
        self.label = label
        self.taskCounter = TaskCounter(serial)
        if label != "":
            ClientLogWriter("用户指定稳定币:" + label)
            if label.endswith("|4"):
                self.isFourTimes = True
            self.coinName = label.strip("|4").strip("|1")

    def GetDefaultCoin(self):
        return self.coinName

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

    def alpha_trade(
        self,
        buy_ratio: float = 0.95,
        buy_markup: float = 1.03,
        sell_discount: float = 0.97,
        step_sleep_s: float = 3.0,
    ) -> Dict[str, Any]:
        """
        返回一个 dict，包含解析结果、下单金额、下单价格、确认坐标等，方便你日志记录/二次处理
        """
        sc = self.dev.screenshot()

        prompt_trade = (
            "帮我提取当前页面的内容,然后帮我获取几个数据 "
            "1:给出限价单设置区价格输入框中间位置的坐标 "
            "2:给出总额(USDT)输入框中间位置的坐标 "
            "3:给出卖出价格(USDT)输入框中间的位置 "
            "4: 给出交易确认区域绿色的按钮(买入 xxx)的中间位置的坐标 "
            "5:给出可用资金的金额 "
            "6:给出币种信息区域里的价格 。 "
            "然后把这个6个结果用逗号分割拼接在一起拼接后的字符串头部添加hyper字样尾部添加byte字样，"
            "示例:hyper(x1,y1),(x2,y2),(x3,y3),(x4,y4),26.97410233 USDT,$0.015911byte,"
            "要和示例的格式保持一致，这样方便我提取"
        )

        resp_trade = self.glm.chat_image_text(sc.base64_data, prompt_trade)
        targets = parse_trade_targets(resp_trade)
        if targets is None:
            raise RuntimeError(f"parse_trade_targets failed. resp={resp_trade}")

        coin_price = targets.coin_price_usd
        available_amount = round(targets.available_usdt * buy_ratio, 2)

        # 1) 输入总金额
        self.dev.tap_rel_1000(*targets.total_usdt_input_center, sc.width, sc.height)
        self.dev.clear_and_type(str(available_amount))
        time.sleep(step_sleep_s)

        # 2) 输入买入价格
        buy_price = coin_price * buy_markup
        self.dev.tap_rel_1000(*targets.price_input_center, sc.width, sc.height)
        self.dev.clear_and_type(str(buy_price))
        time.sleep(step_sleep_s)

        # 3) 输入卖出价格
        sell_price = coin_price * sell_discount
        self.dev.tap_rel_1000(*targets.sell_price_input_center, sc.width, sc.height)
        self.dev.clear_and_type(str(sell_price))
        time.sleep(step_sleep_s)

        # 4) 点击买入按钮
        self.dev.tap_rel_1000(*targets.buy_button_center, sc.width, sc.height)
        time.sleep(1.0)

        # 5) 识别弹窗确认按钮并点击
        sc2 = self.dev.screenshot()
        prompt_confirm = "目前页面上出现了一个弹窗，请给出弹窗的下方黄色的确认按钮的中心位置的坐标"
        resp_confirm = self.glm.chat_image_text(sc2.base64_data, prompt_confirm)
        confirm_xy = extract_confirm_button_xy(resp_confirm)
        if confirm_xy is None:
            raise RuntimeError(f"extract_confirm_button_xy failed. resp={resp_confirm}")

        self.dev.tap_rel_1000(confirm_xy[0], confirm_xy[1], sc2.width, sc2.height)

        return {
            "targets": targets,
            "available_amount": available_amount,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "confirm_xy": confirm_xy,
            "resp_trade_raw": resp_trade,
            "resp_confirm_raw": resp_confirm,
        }


def get_api_key_from_env(env_name: str = "BIGMODEL_API_KEY") -> str:
    v = os.getenv(env_name)
    if not v:
        raise RuntimeError(f"Missing env var {env_name}. e.g. set {env_name}=your_key")
    return v


def ClientLogWriter(text, end="\n"):
    print("INFO::", time.asctime(), text)
