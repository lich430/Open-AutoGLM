#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner import AutoGLMRunner
from phone_agent.device_factory import get_device_factory
import json
import re
from typing import Optional, Tuple

import requests
import re


# 返回首页：
def task_return_homepage(runner: AutoGLMRunner):
    # print(get_nav_home_center_hyper())
    # point = get_nav_home_center_hyper()
    # if point[0] != 0:
    #     prompt = f"""点击位置{point}"""
    #     runner.run(prompt)
    prompt = """打开币安APP. 如果页面底部有导航栏（通常在APP首页底部会有"首页"、"行情"、"交易"、"合约"、"资产"等导航按钮）点击导航栏首页选项，如果页面底部没有导航栏返回上一步"""
    runner.run(prompt)


# 进入alpha交易，具体的操作如下：
def task_enter_alpha_trade(runner: AutoGLMRunner, symbol: str):
    task_return_homepage(runner)

    symbol = (symbol or "").strip()
    if not symbol:
        raise ValueError("symbol 不能为空，例如 'ARTX'")

    prompt = f"""1. 点击页面底部导航栏的行情菜单进入行情页 2. 在行情页的最上方有个搜索框，在搜索框中搜索{symbol} 3. 如果输入框下方的历史记录有{symbol}，就点击它 4. 搜索结果会有多个分类，选择Alpha那个分类 5. 点击进入K线页面 6. 在K线页面的右下角，点击一个黄色交易按钮"""
    #prompt = f"""当前操作的是币安APP  1: 点击页面底部导航栏的行情菜单进入行情页 2:在行情页的最上方有个搜索框请你在搜索框中搜索{symbol}，如果输入框下方的历史记录有{symbol}你就直接点击就好了，不需要输入{symbol}，搜索的结果会有多个分类，你选择alpha那个分类，并点击进入K线页面 3:在K线页面的右下角你会发现一个黄色交易按钮位置大概在左上角(55,315),右下角(324,353)大概这个矩形，点击交易按钮进入alpha交易页面"""
    runner.run(prompt)

# # 重置alpha交易页面设置:
# def task_reset_alpha_trade_page(runner: AutoGLMRunner):
#     prompt = """1：交易模式选择限价模式，在页面的偏上的位置，你会发现有限价和即时两个并排在一起的标签，如果即时处于被选中状态（白色背景）就点击左边的限价，如果限价是被选中状态（白色背景）那就什么也不做。2：交易方向选择买入，在页面的偏上的位置，你会发现有买入行和卖出行两个并排在一起的按钮一左一右，如果买入行按钮是(绿色高亮)的说明已经是买入模式就什么也不做，如果卖出行按钮是(红色高亮)的就意味当前是是卖出模式,需要点击左边的买入"""
#     runner.run(prompt)


# 取消alpha订单：
def task_cancel_alpha_orders(runner: AutoGLMRunner):
    prompt = """1. 滑动一次，滑动 start 位置 [750,800]，end [750,550]，如果页面上有"当前委托"这四个字，就查看页面下方是否有委托的订单 2. 如果有委托的订单，逐个取消订单 3. 取消委托订单完成后，滑动 start [750,400]，end [750,850]"""
    #prompt = """当前是币安app  1:滑动一次,滑动的start位置的[750,800],end[750,550]，如果页面上有 当前委托 这四个字，就查看页面下方是否有委托的订单。2：如果有委托的订单逐个取消订单。3:取消委托订单完成后,滑动的start[750,400]，end[750,850]。"""
    runner.run(prompt)


# 进入合约交易USDT：
def task_enter_futures_usdt(runner: AutoGLMRunner):

    task_return_homepage(runner)

    prompt = """当前是币安app,点击底部导航栏中的合约，进入合约交易页面，合约交易页面上方理应有很多分类，选择U本位分类，如果合约页面上方没有分类，就需要你先向下滑动页面滑动后会出现U本位的分类，如果找不到U本位分类那就一直尝试滑动，不进行下一步的任何动作，直到出现U本位的分类。然后重新尝试选择U本位的分类，如果已经是U本位了那就不用选。大概在页面的最上方你会发现一个****USDT和永续的字样，在永续二字的旁边有一个下拉按钮，点击它，点开下拉按钮后，弹出一个子页面，子页面上有搜索框，你搜索BNBUSDT，搜索的结果分类选择U本位合约，找到BNBUSDT点击它，你会重新回到合约的交易页面"""
    runner.run(prompt)



# 逛广场:
def task_browse_square(runner: AutoGLMRunner):
    task_return_homepage(runner)

    prompt = """当前是币安app,1. 点击发现底部发现按钮 进入发现页面 向下滑动浏览 滑动尽量快速些 滑动几次后 挑一个能看到文字的帖子，点击文字进入帖子(不要点击图片进入)  进入帖子后快速下滑浏览 2. 如过帖子里有其他人评论的话 对这个帖子进行点赞  并根据文章文字的内容做出回复,且内容不超过20个字，然后把要回复的从左下角输入  取消勾选'评论并转发'(前面不要打钩) 点击发送  如过弹出仅限关注才能回复 就选择 取消并返回发现页 如过不提示就点击发送 。3.完成点赞或评论后，点击子页面左上角的返回箭头，返回主页并结束本次任务"""
    runner.run(prompt)


# 看直播：
def task_watch_live(runner: AutoGLMRunner):
    task_return_homepage(runner)

    prompt = """1. 当前是币安app 2. 点击下方'直播'按钮  进入后向下持续滑动浏览 滑动尽量快速些 3. 进入一个直播间 在里面不操作任何内容 待够3-5分钟左右退出直播间 持续下滑一会然后结束任务"""
    runner.run(prompt)



# 使用示例
def task_get_alpha_estimated_volume(runner):
    task_return_homepage(runner)

    prompt = """1.当前是币安APP的页面,点击左上角的三条横杠的按钮进入用户中心 在用户中心页面你会看到"Alpha活动"图标，进入"Alpha活动"页面后点击右上角的三个点菜单会出现弹窗，然后点击弹窗上的刷新功能 完成刷新后向上滑动1次页面 start[750,850], end[750,300] 后结束任务"""
    runner.run(prompt)

    device_factory = get_device_factory()
    device_id = device_factory.list_devices()[0].device_id

    volume = get_today_trade_volume(
        device_factory=device_factory,
        device_id=device_id,
    )

    print("today volume:", volume)

    runner.run("执行2次返回操作(action:back)")

    return volume


def get_today_trade_volume(
    device_factory,
    device_id: str,
    *,
    model: str = "glm-4.6v",
    url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    timeout_s: int = 60,
    return_raw: bool = False,
) -> float | Tuple[float, str]:
    """
    截图 -> 调用 GLM 识别 -> 从返回的 message.content 中提取今天的预估交易量

    返回:
      - return_raw=False: volume(float)
      - return_raw=True : (volume(float), raw_response_text(str))
    """
    screenshot = device_factory.get_screenshot(device_id)

    api_key = "d02cf9e65048471d92c4fd840a280934.OCIg95VIrqTnKboe"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    prompt = '帮我提取"今天"的预估数据中的交易量。在交易量的前面加hyper后面加byte后输出，举例:"hyper1000byte"'

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": screenshot.base64_data}},
                    {"type": "text", "text": prompt},
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

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
    resp.raise_for_status()

    raw_text = resp.text

    # 解析 content
    obj = json.loads(raw_text)
    content = obj["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise RuntimeError(f"GLM content is not str: {type(content)}")

    content = content.strip()

    # 提取 hyperxxxbyte 中的 xxx（数字）
    m = re.search(r"hyper\s*([0-9]+(?:\.[0-9]+)?)\s*byte", content, flags=re.IGNORECASE)
    if not m:
        # 兜底：抓 content 里的第一个数字
        nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", content)
        if not nums:
            raise RuntimeError(f"Cannot parse volume from content: {content!r}")
        volume = float(nums[0])
    else:
        volume = float(m.group(1))

    return (volume, raw_text) if return_raw else volume

def extract_hyper_xy(model_text: str) -> tuple[int, int] | None:
    """
    从模型返回文本中提取 hyper(x,y)byte。
    兼容：模型前后输出了额外字符、换行、引号、json 包裹等情况。
    返回 (x,y) 或 None。
    """
    if not model_text:
        return None

    _HYPER_RE = re.compile(
        r"hyper\s*\(\s*(\d{1,4})\s*,\s*(\d{1,4})\s*\)\s*byte",
        re.IGNORECASE
    )
    # 1) 先直接 regex 抓 hyper(x,y)byte
    m = _HYPER_RE.search(model_text)
    if m:
        x, y = int(m.group(1)), int(m.group(2))
        return x, y

    # 2) 如果模型把内容塞在 JSON 里（比如 {"result":"hyper(1,2)byte"}）
    #    尝试提取 JSON 并再 regex
    #    注意：这里“尽力而为”，避免因非严格 JSON 报错
    try:
        maybe_json = model_text.strip()
        if maybe_json.startswith("{") and maybe_json.endswith("}"):
            obj = json.loads(maybe_json)
            # 常见字段名都试一下
            for k in ("result", "text", "output", "content", "answer"):
                if k in obj and isinstance(obj[k], str):
                    m2 = _HYPER_RE.search(obj[k])
                    if m2:
                        return int(m2.group(1)), int(m2.group(2))
    except Exception:
        pass

    return None


def get_nav_home_center_hyper(
    model: str = "glm-4.6v",
    url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    timeout_s: int = 60,
) -> tuple[int, int]:

    device_factory = get_device_factory()
    device_id = device_factory.list_devices()[0].device_id

    screenshot = device_factory.get_screenshot(device_id)

    api_key = "d02cf9e65048471d92c4fd840a280934.OCIg95VIrqTnKboe"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # prompt = (
    #     "你是一个严格的坐标提取器。\n"
    #     "任务：判断截图底部是否存在导航栏，且导航栏包含五个菜单："
    #     "首页、行情、交易、合约、资产。\n"
    #     "如果存在：输出【导航栏最左侧第一个菜单（首页）的中心点】坐标。\n"
    #     "如果不存在：输出 (0,0)。\n\n"
    #     "输出必须且只能是以下格式（不要任何多余字符/解释/换行）：\n"
    #     "hyper(x,y)byte\n"
    #     "其中 x,y 为 0~1000 的整数（相对整张图归一化坐标）。"
    # )

    prompt = """ 你分析下当前页面的内容 如果页面底部存在导航栏(通常在APP首页底部会有"首页"、"行情"、"交易"、"合约"、"资产"等导航按钮)则返回底部导航栏首页按钮的中心坐标位置,如果页面上没有导航栏返回(0,0)。请在返回结果前面加一个hyper后面加byte输出，例如:hyper(x,y)byte """

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": screenshot.base64_data}},
                    {"type": "text", "text": prompt},
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

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
    resp.raise_for_status()

    raw_text = resp.text

    # 解析 content
    obj = json.loads(raw_text)
    print(f"""obj:{obj}""")
    content = obj["choices"][0]["message"]["content"]
    print(f"""返回内容: {content}""")
    if not isinstance(content, str):
        raise RuntimeError(f"GLM content is not str: {type(content)}")

    content = content.strip()

    point = extract_hyper_xy(content)
    if point[0] != 0:
        x = int(point[0] / 1000 * screenshot.width)
        y = int(point[1] / 1000 * screenshot.height)
        device_factory.tap(x, y, device_id)

    return point


def task_spot_buy_bnb(runner):
    task_return_homepage(runner)
    prompt = """
当前是币安app的首页，按照以下步骤执行: 1: 点击底部导航栏的行情选项 2：在行情页面顶部有一个搜索框,搜索"BNB",如果输入框下方的历史记录有BNB你就直接点击就好了，不需要输入BNB了 3：搜索的结果中有很多分类分别是"所有，现货，Alpha,合约，期权",选择现货这个分类 4：然后点击现货分类中的第一个搜索结果，然后进入行情页面。 5：行情页面的右下方有两个按钮分别是"买入，卖出"，点击绿色的买入按钮，进入交易页面。 6：在交易页面有一个总金额的输入框，输入10。然后点击买入BNB并确定下单
"""
    runner.run(prompt)


def main():
    runner = AutoGLMRunner()
    # task_spot_buy_bnb(runner)
    # return
    #task_switch_to_exchange(runner)
    # task_return_homepage(runner)

    # # alpha交易相关的
    # #
    # task_enter_alpha_trade(runner, "RLS")
    # task_reset_alpha_trade_page(runner)
    # task_cancel_alpha_orders(runner)
    # task_place_alpha_buy_order(runner,"RLS")


    # # 进入合约页面
    # task_enter_futures_usdt(runner)
    #
    # # 逛广场
    #task_browse_square(runner)

    volume = task_get_alpha_estimated_volume(runner)
    print(f"volume:{volume}")

    # #看直播
    #task_watch_live(runner)


if __name__ == "__main__":
    main()
