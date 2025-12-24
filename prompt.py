#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner import AutoGLMRunner
import io
import contextlib
import re

def task_switch_to_exchange(runner: AutoGLMRunner):
    prompt = """当前操作的是币安APP 如果页面"顶部"有两个按钮分别是"交易平台和钱包"，如果交易平台是被选中的白色背景那就什么也不做，否则就点击交易平台按钮，最多操作1步后就立即结束任务"""
    runner.run(prompt)

# 返回首页：
def task_return_homepage(runner: AutoGLMRunner):

    prompt = """当前操作的是币安APP 1:如果页面有底部导航栏：首页、行情、交易、合约、资产，双击导航栏的首页选项，点击一次后立即结束任务不用管页面是否变化。 2: 如果页面下方没有导航栏且的左上角有返回箭头或者右上角有关闭按钮(X形状)，点击返回箭头或则关闭按钮重复该操直到页面出现了导航栏，双击导航栏的首页选项，点击一次后立即结束任务不用管页面是否变化"""
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


# 执行购买：
def task_place_alpha_buy_order(runner: AutoGLMRunner, symbol: str):
    #task_cancel_alpha_orders(runner)
    prompt = """
当前页面布局如下：
1. 顶部显示"现货"、"杠杆"、"交易机器人"、"C2C"、"Alpha"等标签，当前在"Alpha"页面
2. 显示的是"xxxx"的交易界面
3. 价格列表在右侧，从上到下显示
4. 底部显示"当前价格: ¥xxxxxx xx%"
5. 有"限价"和"即时"两个选项，当前选择的是"限价"
6. 有"买入"和"卖出行"两个按钮
7. 有"限价单"下拉框
8. 有"价格"输入框，显示"xxxxxxxxxx"
9. 有"建议价格 xxxxxxx"
10. 有"数量(XXXXX)"输入框
11. 有"总额(USDT)"输入框
12. 有"反向订单"选项（已勾选）
13. 有"卖出行价(USDT)"输入框
14. 有"可用 xxxxxxx USDT"显示
15. 有"预估手续费"
16. 有"买入 XXXX"绿色按钮
17. 有"成本价 xxxxxx USDT"

请帮我完成以下任务：
1. 价格输入框的右侧2/5是一个下拉框，左侧的3/5才是有效的输入框区域，你只能点击左侧的3/5区域否则会弹出USDT和USDC选择框,把当前价格的105%填入价格输入框。
    """
    #prompt = f"""交易页面上内容如下： 1.顶部有"现货"、"杠杆"、"交易机器人"、"C2C"、"Alpha"等标签，当前在"Alpha"页面 2.显示的是"ESPORTS"的交易界面 3.价格列表在右侧，从上到下显示 4.当前显示的最新价格是：XXXXX（在底部显示为"当前价格"） 5.有"限价"和"即时"两个选项，当前选择的是"限价" 6.有"买入"和"卖出行"两个按钮 6.5.有"限价单"下拉框. 7.有"价格"输入框。请你帮我把最新价格的1.05倍填入该输入框 8.有"建议价格 XXXXXX" (右边显示了价格) 9.有"数量(XXXX)"输入框 9.有"总额(USDT)"输入框。请你帮我把可用金额填入该输入框 10.有"反向订单"选项（已勾选） 11.有"卖出行价(USDT)"输入框。 请你帮我把最新价格的的0.95倍填入该输入框 12.有"可用 xxxxx USDT"显示 13.有"预估手续费" 14.有"成本价 xxxx USDT"。 请帮我完成以上需要你帮忙的任务"""
    # prompt = f"""当前是币安app的alpha交易页面，1: 最新价格的定义--在页面的右侧有一个价格列表从上倒下的顺序第1个价格就是最新价。 2：将最新价格的1.03倍填入买入价格输入框---大概位置在建议价格上方,在该输入框的内部有价格的字样点击该价格字样下方输入框的位置，触发输入光标。3.可用资金--页面上显示可用的数据，例如: 可用 XXXXXX。可用资金保留两位有效数字填入USDT总额输入框， 点击总额输入框中间的位置，触发输入光标。4: 将最新价格的0.95倍填入反向订单价格输入框---该输入框在页面上上的x轴的大概坐标范围位于 反向订单 4个字的下方和 可用 2个字的上方, 点击反向订单价格输入框中间侧的位置，触发输入光标,填入反向价格。5.最后点击页面偏下方的 买入 {symbol} 按钮, 如果弹出确认框,你需要点击确认按钮。"""
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

    prompt = """1. 当前是币安app 2. 点击下方'直播'按钮  进入后向下持续滑动浏览 滑动尽量快速些 3. 进入一个直播间 在里面不操作任何内容 待够5分钟左右 然后退出直播间 持续下滑一会 然后重复上面操作5次"""
    runner.run(prompt)

# 获取交易金额：

def run_and_capture_prints(runner, prompt: str):
    # result = runner.run(prompt)
    # return
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = runner.run(prompt)   # runner.run 原本会 print，这里会被写入 buf
    logs = buf.getvalue()
    return result, logs

def extract_trade_volume(logs: str):
    # 提取 "预估" 后面跟随的 ¥ 或 $ 的金额
    m = re.search(r"预估\s*([\¥\$])([0-9]+(?:\.[0-9]+)?)", logs)
    if not m:
        return None
    # 返回提取的金额（以浮动类型返回）
    return float(m.group(2))  # 这里改为返回数字部分，而不是货币符号




# 使用示例
def task_get_alpha_estimated_volume(runner):
    task_return_homepage(runner)

    prompt = """当前是币安app首页,1:首页页面的顶部，在页面的上方你会看到 Alpha活动 的图标,点击它进入 Alpha活动 页面，进入Alpha活动页后,后点击右上角的三个点的菜单会出现一个弹窗，然后继续点击弹窗上的刷新功能， 2.滑动1次页面，start位置的[750,800],end[750,500]，滑动后会看页面有[预估 $xxxx]的内容,旁边有个向右的箭头,点击向右的箭头弹出的页面就可以清晰的看到预估的交易量。完成以上操作后点击左上角的返回箭头或则右上角的X按钮,退回至首页 """

    result, logs = run_and_capture_prints(runner, prompt)

    volume = extract_trade_volume(logs)
    print("捕获到的volume:", volume)
    # 你也可以把 logs 存文件，或进一步解析
    return volume

def task_spot_buy_bnb(runner):
    task_return_homepage(runner)
    prompt = """
当前是币安app的首页，按照以下步骤执行: 1: 点击底部导航栏的行情选项 2：在行情页面顶部有一个搜索框,搜索"BNB",如果输入框下方的历史记录有BNB你就直接点击就好了，不需要输入BNB了 3：搜索的结果中有很多分类分别是"所有，现货，Alpha,合约，期权",选择现货这个分类 4：然后点击现货分类中的第一个搜索结果，然后进入行情页面。 5：行情页面的右下方有两个按钮分别是"买入，卖出"，点击绿色的买入按钮，进入交易页面。 6：在交易页面有一个总金额的输入框，输入10。然后点击买入BNB并确定下单
"""
    runner.run(prompt)


def main():
    runner = AutoGLMRunner()
    task_spot_buy_bnb(runner)
    return
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

    # volume = task_get_alpha_estimated_volume(runner)
    # print(f"volume:{volume}")

    # #看直播
    # task_watch_live(runner)


if __name__ == "__main__":
    main()
