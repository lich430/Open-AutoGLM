from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

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
