from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

def ensure_aware(dt: datetime, target_tz: timezone = timezone.utc) -> datetime:
    if dt.tzinfo is None:
        logger.warning(
            f"【时间工具】检测到naive datetime对象，自动转换为UTC aware。"
            f"原始值: {dt}, 类型: {type(dt)}, tzinfo: {dt.tzinfo}"
        )
        return dt.replace(tzinfo=target_tz)
    return dt.astimezone(target_tz)

def parse_iso_datetime(datetime_str: str) -> datetime:
    try:
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str.replace('Z', '+00:00')
        return datetime.fromisoformat(datetime_str)
    except Exception as e:
        logger.error(
            f"【时间工具】ISO datetime解析失败。"
            f"输入: {datetime_str}, 错误: {e}"
        )
        raise

def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        logger.warning(
            f"【时间工具】to_utc收到naive datetime，假设为UTC。"
            f"值: {dt}"
        )
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_and_normalize_to_utc(time_value) -> Optional[datetime]:
    if time_value is None:
        return None
    
    if isinstance(time_value, datetime):
        return to_utc(time_value)
    
    if isinstance(time_value, str):
        parsed = parse_iso_datetime(time_value)
        return to_utc(parsed)
    
    logger.error(
        f"【时间工具】无法解析的时间类型。"
        f"值: {time_value}, 类型: {type(time_value)}"
    )
    raise TypeError(f"不支持的时间类型: {type(time_value)}")

def calculate_hours_between(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    if end_time is None:
        end_time = get_utc_now()
    
    try:
        start_utc = ensure_aware(start_time, timezone.utc)
        end_utc = ensure_aware(end_time, timezone.utc)
        
        duration = end_utc - start_utc
        return max(0, duration.total_seconds() / 3600)
    
    except TypeError as e:
        logger.error(
            f"【时间工具】计算时间差时发生类型错误。"
            f"开始时间: {start_time}, 类型: {type(start_time)}, tzinfo: {getattr(start_time, 'tzinfo', None)}, "
            f"结束时间: {end_time}, 类型: {type(end_time)}, tzinfo: {getattr(end_time, 'tzinfo', None)}, "
            f"错误: {e}"
        )
        return 0.0
    
    except Exception as e:
        logger.error(
            f"【时间工具】计算时间差时发生未知错误。"
            f"开始时间: {start_time}, 结束时间: {end_time}, 错误: {e}"
        )
        return 0.0

def to_local_time(dt: datetime, local_tz: timezone = None) -> datetime:
    if local_tz is None:
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
    
    if dt.tzinfo is None:
        logger.warning(
            f"【时间工具】to_local_time收到naive datetime，先假设为UTC再转换。"
            f"值: {dt}"
        )
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(local_tz)

def format_iso(dt: datetime, include_timezone: bool = True) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    if include_timezone:
        return dt.isoformat().replace('+00:00', 'Z')
    
    return dt.strftime('%Y-%m-%dT%H:%M:%S')