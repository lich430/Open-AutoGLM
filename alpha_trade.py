# run_trade.py
from phone_agent.device_factory import get_device_factory

from hyper_glm_trade import DeviceOps, GLMVisionClient, HyperTradeBot, get_api_key_from_env


def main():
    device_factory = get_device_factory()
    devices = device_factory.list_devices()
    if not devices:
        raise RuntimeError("No devices detected")

    device_id = devices[0].device_id

    api_key = get_api_key_from_env("BIGMODEL_API_KEY")  # 推荐用环境变量
    glm = GLMVisionClient(api_key=api_key, model="glm-4.6v")

    dev = DeviceOps(device_factory, device_id)
    bot = HyperTradeBot(device_id, "", 100, glm, dev)

    result = bot.alpha_trade("ESPORTS", buy_ratio=0.95, buy_markup=1.03, sell_discount=0.97)
    print("DONE:", result)


if __name__ == "__main__":
    main()
