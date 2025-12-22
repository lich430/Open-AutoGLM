#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.device_factory import DeviceFactory, get_device_factory
from phone_agent.model import ModelConfig


@dataclass
class RunnerConfig:
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    api_key: str = "d02cf9e65048471d92c4fd840a280934.OCIg95VIrqTnKboe"
    model: str = "autoglm-phone"
    lang: str = "cn"
    max_steps: int = 20
    verbose: bool = True


class AutoGLMRunner:
    """
    AutoGLM 可复用执行器：
    - check_model_api(): 检查模型 API 是否可用
    - resolve_device_id(): device_id 为空时取第一个设备
    - run(): 执行任务
    """

    def __init__(self, config: Optional[RunnerConfig] = None):
        self.config = config or RunnerConfig()

    def check_model_api(self) -> bool:
        base_url = self.config.base_url
        model_name = self.config.model
        api_key = self.config.api_key

        print("🔍 Checking model API...")
        print("-" * 50)
        print(f"1. Checking API connectivity ({base_url})...", end=" ")

        try:
            client = OpenAI(base_url=base_url, api_key=api_key, timeout=30.0)
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0.0,
                stream=False,
            )

            if response.choices and len(response.choices) > 0:
                print("✅ OK")
                print("-" * 50)
                print("✅ Model API checks passed!\n")
                return True

            print("❌ FAILED")
            print("   Error: Received empty response from API")
            print("-" * 50)
            print("❌ Model API check failed. Please fix the issues above.")
            return False

        except Exception as e:
            print("❌ FAILED")
            error_msg = str(e)

            if "Connection refused" in error_msg or "Connection error" in error_msg:
                print(f"   Error: Cannot connect to {base_url}")
                print("   Solution:")
                print("     1. Check if the model server is running")
                print("     2. Verify the base URL is correct")
                print(f"     3. Try: curl {base_url}/chat/completions")
            elif "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                print(f"   Error: Connection to {base_url} timed out")
                print("   Solution:")
                print("     1. Check your network connection")
                print("     2. Verify the server is responding")
            elif (
                "Name or service not known" in error_msg
                or "nodename nor servname" in error_msg
            ):
                print("   Error: Cannot resolve hostname")
                print("   Solution:")
                print("     1. Check the URL is correct")
                print("     2. Verify DNS settings")
            else:
                print(f"   Error: {error_msg}")

            print("-" * 50)
            print("❌ Model API check failed. Please fix the issues above.")
            return False

    def resolve_device_id(self, device_id: Optional[str]) -> str:
        if device_id and str(device_id).strip():
            return str(device_id).strip()

        device_factory = get_device_factory()
        devices = device_factory.list_devices()
        if not devices:
            raise RuntimeError(
                "device_id is empty and no devices were detected by device_factory.list_devices()"
            )

        return devices[0].device_id

    def _build_agent(self, resolved_device_id: str) -> PhoneAgent:
        cfg = self.config

        model_config = ModelConfig(
            base_url=cfg.base_url,
            model_name=cfg.model,
            api_key=cfg.api_key,
            lang=cfg.lang,
        )

        agent_config = AgentConfig(
            max_steps=cfg.max_steps,
            device_id=resolved_device_id,
            verbose=cfg.verbose,
            lang=cfg.lang,
        )

        return PhoneAgent(model_config=model_config, agent_config=agent_config)

    def build_agent(self) -> PhoneAgent:
        resolved_device_id = self.resolve_device_id(None)
        cfg = self.config

        model_config = ModelConfig(
            base_url=cfg.base_url,
            model_name=cfg.model,
            api_key=cfg.api_key,
            lang=cfg.lang,
        )

        agent_config = AgentConfig(
            max_steps=cfg.max_steps,
            device_id=resolved_device_id,
            verbose=cfg.verbose,
            lang=cfg.lang,
        )

        return PhoneAgent(model_config=model_config, agent_config=agent_config)

    def get_device_factory(self) -> DeviceFactory:
        return get_device_factory()

    def run(self, task: str, device_id: Optional[str] = None, check_api: bool = True) -> str:
        if task is None or not str(task).strip():
            raise ValueError("task must not be empty")

        if check_api and not self.check_model_api():
            raise RuntimeError("Model API check failed")

        resolved_device_id = self.resolve_device_id(device_id)
        agent = self._build_agent(resolved_device_id)

        print("=" * 50)
        print(f"Model: {self.config.model}")
        print(f"Base URL: {self.config.base_url}")
        print(f"Max Steps: {self.config.max_steps}")
        print(f"Language: {self.config.lang}")
        print(f"Device: {resolved_device_id}")
        print("=" * 50)

        print(f"\nTask: {task}\n")
        result = agent.run(str(task).strip())
        print(f"\nResult: {result}")
        return result
