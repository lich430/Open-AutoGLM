#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner import AutoGLMRunner
from phone_agent import PhoneAgent


# 返回首页：
def task_return_homepage(runner: PhoneAgent):
    prompt = """1 检查当前页面底部是否有导航栏，如果底部没有导航栏关闭当前页面或则返回上一步，重复该操作。2：发现底部导航栏后，点击首页。"""
    runner.run(prompt)


# 进入alpha交易，具体的操作如下：
def task_enter_alpha_trade(runner: PhoneAgent, symbol: str):
    task_return_homepage(runner)

    symbol = (symbol or "").strip()
    if not symbol:
        raise ValueError("symbol 不能为空，例如 'ARTX'")

    prompt = f"""进入币安的首页, 点击页面底部导航栏的行情菜单进入行情页，在行情页的最上方有个搜索框请你在搜索框中搜索{symbol}，如果输入框下方的历史记录有{symbol}你就直接点击就好了，不需要输入{symbol}，,搜索的结果会有多个分类，你选择alpha那个分类，并点击进去，点击后会进入K线页面，在K线页面你会发现一个交易按钮，点击交易按钮进入alpha交易页面"""
    runner.run(prompt)

# 重置alpha交易页面设置:
def task_reset_alpha_trade_page(runner: PhoneAgent):
    prompt = """当前页面是alpah交易的页面  1：交易模式选择限价模式。2：交易方向选择买入: 在页面的上半部分你会发现有买入和卖出两个按钮，点击买入行按钮，不要点击卖出行按钮。"""
    runner.run(prompt)


# 执行购买：
def task_place_alpha_buy_order(runner: PhoneAgent, symbol: str):
    task_cancel_alpha_orders(runner)

    prompt = f"""当前是alpha交易页面，1: 页面上有建议价格的的内容，例如[建议价格 xxxxxxx],你帮我点击xxxxxxx这个数字位置。目前发现你点击的位置偶尔不对，所以你需要把获取位置之后点击xxxxxxx重复3次。2: 在当前页面有可用资金的数据，不允许你点击[可用资金 XXXXXXXX]这个数据区域也不要点击该数据后面的加号。把该可用资金保留两位有效小数填入 总额(USDT)输入框。3: 页面上有建议价格A。获取价格B=A*0.95,把价格B填入反向订单复选框下方的 卖出价格(USDT) 输入框, 4: 任务1,2,3都完成后点击 买入 {symbol} 按钮执行买入，弹出确认框时你需要点击确认按钮。"""
    runner.run(prompt)


# 取消alpha订单：
def task_cancel_alpha_orders(runner: PhoneAgent):
    prompt = """当前页面是alpah交易的页面,千万不要点击反向订单那个复选框, 仅限于下方的【当前委托】才能确定是否已经有有订单，千万不要傻傻的去点击反向订单。 如果页面上看不到当前委托你就向下滑动页面，看到当前委托后下方的内容后如果发现有未完成的委托单就取消所有的单子，取消完成后向连续上滑动页面到顶部"""
    runner.run(prompt)


# 点击alpha交易页面的组件：
def task_click_alpha_controls(runner: PhoneAgent):
    prompt = """进入币安app，在当前alpla交易页面点击以下几处位置1：点击价格输入框，2：点击总额(USDT)输入框，3：点击卖出价格输入框，4：点击页面偏下方的的买入 XXX的按钮， 5：点击右下角输入法的完成按钮"""
    runner.run(prompt)



# 获取alpha交易页面最新价格
def task_get_alpha_latest_price(runner: PhoneAgent):
    prompt = """进入币安app,在当前alpha交易页面获取最新价格，页面的右侧有一个订单薄，订单薄的从上到下的顺序第一个价格就是最新价格， 请在最新价格的前后分别加上######。"""
    runner.run(prompt)




# 进入合约交易USDT：
def task_enter_futures_usdt(runner: PhoneAgent):

    task_return_homepage(runner)

    prompt = """点击底部导航栏中的合约，进入合约交易页面，合约交易页面上方理应有很多分类，选择U本位分类，如果合约页面上方没有分类，就需要你先向下滑动页面滑动后会出现U本位的分类，如果找不到U本位分类那就一直尝试滑动，不进行下一步的任何动作，直到出现U本位的分类。然后重新尝试选择U本位的分类，如果已经是U本位了那就不用选。大概在页面的最上方你会发现一个****USDT和永续的字样，在永续二字的旁边有一个下拉按钮，点击它，点开下拉按钮后，弹出一个子页面，子页面上有搜索框，你搜索BNBUSDT，搜索的结果分类选择U本位合约，找到BNBUSDT点击它，你会重新回到合约的交易页面"""
    runner.run(prompt)



# 逛广场:
def task_browse_square(runner: PhoneAgent):
    task_return_homepage(runner)

    prompt = """1. 点击发现底部发现按钮 进入发现页面 向下滑动浏览 滑动尽量快速些 滑动几次后 挑一个能看到文字的帖子，点击文字进入帖子(不要点击图片进入)  进入帖子后快速下滑浏览 2. 如过帖子里有其他人评论的话 对这个帖子进行点赞  并根据文章文字的内容做出回复,且内容不超过20个字，然后把要回复的从左下角输入  取消勾选'评论并转发'(前面不要打钩) 点击发送  如过弹出仅限关注才能回复 就选择 取消并返回发现页 如过不提示就点击发送  完成后返回发现页 。完成点赞或评论后返回主页并结束本次任务"""
    runner.run(prompt)


# 看直播：
def task_watch_live(runner: PhoneAgent):
    task_return_homepage(runner)

    prompt = """1. 打开币安app 进入首页 2. 点击下方'直播'按钮  进入后向下持续滑动浏览 滑动尽量快速些 3. 进入一个直播间 在里面不操作任何内容 待够5分钟左右 然后退出直播间 持续下滑一会 然后重复上面操作5次"""
    runner.run(prompt)


def main():
    runner = AutoGLMRunner()

    # # alpha交易相关的
    # #
    # task_enter_alpha_trade(runner, "RLS")
    # task_reset_alpha_trade_page(runner)

    # task_place_alpha_buy_order(runner,"TTD")

    # # 获取alpha交易页面的数据
    # task_get_alpha_latest_price(runner)
    # task_click_alpha_controls(runner)


    # # 进入合约页面
    # task_enter_futures_usdt(runner)
    #
    # # 逛广场
    task_browse_square(runner)

    # #看直播
    # task_watch_live(runner)


if __name__ == "__main__":
    main()
