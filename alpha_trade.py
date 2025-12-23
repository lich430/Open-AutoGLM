import requests

from phone_agent.device_factory import get_device_factory

import re
from typing import Optional, Dict, Tuple

import json
import re
from typing import Any, Dict, Optional, Tuple


def parse_glm_response_text(resp_text: str) -> Optional[Dict[str, Any]]:

    try:
        obj = json.loads(resp_text)
    except json.JSONDecodeError:
        return None

    try:
        content = obj["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None

    if not isinstance(content, str):
        return None

    # content 里可能有开头换行
    content = content.strip()

    # 1) 坐标：取前三个 (x,y)
    coords = re.findall(r"\((\d+)\s*,\s*(\d+)\)", content)
    if len(coords) < 4:
        return None

    c1 = (int(coords[0][0]), int(coords[0][1]))
    c2 = (int(coords[1][0]), int(coords[1][1]))
    c3 = (int(coords[2][0]), int(coords[2][1]))
    c4 = (int(coords[3][0]), int(coords[3][1]))

    # 2) 可用资金："... ,26.97410233 USDT, ..."
    m_avail = re.search(r",\s*([0-9]+(?:\.[0-9]+)?)\s*USDT\s*,", content, flags=re.IGNORECASE)
    if not m_avail:
        return None
    available_usdt = float(m_avail.group(1))

    # 3) 币价："... ,$0.016087byte"
    m_price = re.search(r",\s*\$\s*([0-9]+(?:\.[0-9]+)?)\s*byte\s*$", content, flags=re.IGNORECASE)
    if not m_price:
        return None
    coin_price_usd = float(m_price.group(1))

    return {
        #"content": content,
        "price_input_center": c1,
        "total_usdt_input_center": c2,
        "sell_price_input_center": c3,
        "buy_button_center":c4,
        "available_usdt": available_usdt,
        "coin_price_usd": coin_price_usd,
    }

def extract_confirm_button_xy(resp_text: str) -> Optional[Tuple[int, int]]:
    """
    从 requests.post(...).text 的完整 JSON 响应中提取确认按钮中心坐标 (x, y)

    期望 message.content 类似：
      "\\n[[499, 877]]"
    也兼容：
      "[499,877]" / "499,877" / "x=499, y=877" 等

    返回：(x, y) 或 None
    """
    # 1) 解析外层 JSON
    try:
        obj = json.loads(resp_text)
    except json.JSONDecodeError:
        return None

    # 2) 取出 content
    try:
        content = obj["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None

    if not isinstance(content, str):
        return None

    content = content.strip()

    # 3) 优先：尝试把 content 当作“JSON/字面量数组”解析（[[x,y]] 或 [x,y]）
    #    注意：content 可能是 "\n[[499, 877]]" 这种，strip 后可直接 json.loads
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

    # 4) 再兜底：正则抓取前两个数字
    nums = re.findall(r"-?\d+(?:\.\d+)?", content)
    if len(nums) >= 2:
        x = int(round(float(nums[0])))
        y = int(round(float(nums[1])))
        return x, y

    return None

def tap(x1,y1,screenshot_width,screenshot_height):
    x = int(x1 / 1000 * screenshot_width)
    y = int(y1 / 1000 * screenshot_height)

    device_factory.tap(x, y, device_id)


url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

device_factory = get_device_factory()
devices = device_factory.list_devices()
if not devices:
    raise RuntimeError(
        "device_id is empty and no devices were detected by device_factory.list_devices()"
    )

device_id = devices[0].device_id

headers = {
    "Authorization": "Bearer d02cf9e65048471d92c4fd840a280934.OCIg95VIrqTnKboe",
    "Content-Type": "application/json"
}



screenshot = device_factory.get_screenshot(device_id)

payload = {
    "model": "glm-4.6v",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url":screenshot.base64_data}
                },
                {
                    "type": "text",
                    "text": "帮我提取当前页面的内容,然后帮我获取几个数据 1:给出限价单设置区价格输入框中间位置的坐标 2:给出总额(USDT)输入框中间位置的坐标 3:给出卖出价格(USDT)输入框中间的位置 4: 给出交易确认区域绿色的按钮(买入 xxx)的中间位置的坐标 5:给出可用资金的金额 6:给出币种信息区域里的价格 。 然后把这个6个结果用逗号分割拼接在一起拼接后的字符串头部添加hyper字样尾部添加byte字样，示例:hyper(x1,y1),(x2,y2),(x3,y3),(x4,y4),26.97410233 USDT,$0.015911byte,要和示例的格式保持一致，这样方便我提取"
                }
            ]
        }
    ],
    "stream": False,
    "thinking": {
        "type": "enabled",
        "clear_thinking": True
    },
    "do_sample": True,
    "temperature": 1,
    "top_p": 0.95,
    "tool_stream": False,
    "response_format": { "type": "text" }
}

#print(f"payload:{payload}")

response = requests.post(url, json=payload, headers=headers)
print(response.text)


print("准备开始解析坐标:")
# 示例
#content = "hyper(180,295),(180,365),(180,435),26.97410233 USDT,$0.015911byte"
#print(parse_glm_response_text(response.text))

result = parse_glm_response_text(response.text)
print(f"result:{result}")
coin_price_usd = result["coin_price_usd"]

# 1. 输入总金额
total_usdt_input_center = result["total_usdt_input_center"]
available_amount =  round(result["available_usdt"] * 0.95,2)
print(f"准备购买金额:{available_amount}")
tap(total_usdt_input_center[0],total_usdt_input_center[1], screenshot.width, screenshot.height)
device_factory.clear_text(device_id)
device_factory.type_text(str(available_amount),device_id)

#2 输入买入价格
price_input_center = result["price_input_center"]
price_input_value =  coin_price_usd * 1.03
print(f"准备输入买入价格:{price_input_value}")
tap(price_input_center[0],price_input_center[1], screenshot.width, screenshot.height)
device_factory.clear_text(device_id)
device_factory.type_text(str(price_input_value),device_id)

#3 输入反向订单卖出价格

sell_price_input_center = result["sell_price_input_center"]
sell_price_input_value =  coin_price_usd * 0.97
print(f"准备输入卖出价格:{sell_price_input_value}")
tap(sell_price_input_center[0],sell_price_input_center[1], screenshot.width, screenshot.height)
device_factory.clear_text(device_id)
device_factory.type_text(str(sell_price_input_value),device_id)

#4 点击买入确认按钮
buy_button_center = result["buy_button_center"]
tap(buy_button_center[0],buy_button_center[1], screenshot.width, screenshot.height)


screenshot = device_factory.get_screenshot(device_id)
payload_confirm = {
    "model": "glm-4.6v",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url":screenshot.base64_data}
                },
                {
                    "type": "text",
                    "text": "目前页面上出现了一个弹窗，请给出弹窗的下方黄色的确认按钮的中心位置的坐标"
                }
            ]
        }
    ],
    "stream": False,
    "thinking": {
        "type": "enabled",
        "clear_thinking": True
    },
    "do_sample": True,
    "temperature": 1,
    "top_p": 0.95,
    "tool_stream": False,
    "response_format": { "type": "text" }
}
response_confirm = requests.post(url, json=payload_confirm, headers=headers)
print(response_confirm.text)
confirm_point = extract_confirm_button_xy(response_confirm.text)
print(f"弹窗确认按钮的位置:{confirm_point}")
tap(confirm_point[0],confirm_point[1], screenshot.width, screenshot.height)



