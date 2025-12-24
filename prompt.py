#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner import AutoGLMRunner
from phone_agent.device_factory import get_device_factory
import json
import re
from typing import Optional, Tuple

import requests
import re

def task_switch_to_exchange(runner: AutoGLMRunner):
    prompt = """当前操作的是币安APP 如果页面"顶部"有两个按钮分别是"交易平台和钱包"，如果交易平台是被选中的白色背景那就什么也不做，否则就点击交易平台按钮，最多操作1步后就立即结束任务"""
    runner.run(prompt)

# 返回首页：
def task_return_homepage(runner: AutoGLMRunner):

    prompt = """当前操作的是币安APP 1:如果页面有底部导航栏：首页、行情、交易、合约、资产，点击导航栏的首页选项，点击一次后立即结束任务不用管页面是否变化。 2: 如果页面下方没有导航栏且的左上角有返回箭头或者右上角有关闭按钮(X形状)，点击返回箭头或则关闭按钮重复该操直到页面出现了导航栏，点击导航栏的首页选项，点击一次后立即结束任务不用管页面是否变化"""
    runner.run(prompt)

    task_switch_to_exchange(runner)


# 进入alpha交易，具体的操作如下：
def task_enter_alpha_trade(runner: AutoGLMRunner, symbol: str):
    task_return_homepage(runner)

    symbol = (symbol or "").strip()
    if not symbol:
        raise ValueError("symbol 不能为空，例如 'ARTX'")

    prompt = f"""进入币安的首页, 点击页面底部导航栏的行情菜单进入行情页，在行情页的最上方有个搜索框请你在搜索框中搜索{symbol}，如果输入框下方的历史记录有{symbol}你就直接点击就好了，不需要输入{symbol}，,搜索的结果会有多个分类，你选择alpha那个分类，并点击进入K线页面，在K线页面的右下角你会发现一个黄色交易按钮位置大概在左上角(55,315),右下角(324,353)大概这个矩形，点击交易按钮进入alpha交易页面"""
    runner.run(prompt)

# 重置alpha交易页面设置:
def task_reset_alpha_trade_page(runner: AutoGLMRunner):
    prompt = """当前页面是币安app的alpah交易的页面  1：交易模式选择限价模式，在页面的偏上的位置，你会发现有限价和即时两个并排在一起的标签，如果即时处于被选中状态（白色背景）就点击左边的限价，如果限价是被选中状态（白色背景）那就什么也不做。2：交易方向选择买入，在页面的偏上的位置，你会发现有买入行和卖出行两个并排在一起的按钮一左一右，如果买入行按钮是(绿色高亮)的说明已经是买入模式就什么也不做，如果卖出行按钮是(红色高亮)的就意味当前是是卖出模式,需要点击左边的买入"""
    runner.run(prompt)


# 取消alpha订单：
def task_cancel_alpha_orders(runner: AutoGLMRunner):
    prompt = """当前是币安app的alpha交易页面,1:滑动一次,滑动的start位置的[750,800],end[750,550]，如果页面上有 当前委托 这四个字，就查看页面下方是否有委托的订单。2：如果有委托的订单逐个取消订单。3:取消委托订单完成后,滑动的start[750,400]，end[750,850]。"""
    runner.run(prompt)


# 点击alpha交易页面的组件：
def task_click_alpha_controls(runner: AutoGLMRunner):
    prompt = """进入币安app，在当前alpla交易页面点击以下几处位置1：点击价格输入框，2：点击总额(USDT)输入框，3：点击卖出价格输入框，4：点击页面偏下方的的买入 XXX的按钮， 5：点击右下角输入法的完成按钮"""
    runner.run(prompt)



# 获取alpha交易页面最新价格
def task_get_alpha_latest_price(runner: AutoGLMRunner):
    prompt = """进入币安app,在当前alpha交易页面获取最新价格，页面的右侧有一个订单薄，订单薄的从上到下的顺序第一个价格就是最新价格， 请在最新价格的前后分别加上######。"""
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

    prompt = """当前是币安app 1:连续滑动三次start位置[750,850],end位置[750,300]，然后双击("action": "Double Tap")左下角的首页菜单。2:点击页面的上方的"Alpha活动"的图标，进入Alpha活动页后点击右上角的三个点的菜单会出现一个弹窗，然后继续点击弹窗上的刷新功能， 3.向上滑动1次页面，start位置的[750,850],end[750,300],然后结束任务"""
    runner.run(prompt)

    device_factory = get_device_factory()
    device_id = device_factory.list_devices()[0].device_id

    volume = get_today_trade_volume(
        device_factory=device_factory,
        device_id=device_id,
    )

    print("today volume:", volume)

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
    #task_return_homepage(runner)

    # # alpha交易相关的
    # #
    # task_enter_alpha_trade(runner, "RLS")
    # task_reset_alpha_trade_page(runner)
    # task_cancel_alpha_orders(runner)
    # task_place_alpha_buy_order(runner,"RLS")

    # # 获取alpha交易页面的数据
    # task_get_alpha_latest_price(runner)
    # task_click_alpha_controls(runner)


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
