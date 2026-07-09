import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from app.utils.time_utils import (
    get_utc_now,
    ensure_aware,
    parse_iso_datetime,
    to_utc,
    parse_and_normalize_to_utc,
    calculate_hours_between,
    format_iso
)

def test_get_utc_now():
    now = get_utc_now()
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc
    print("✓ test_get_utc_now: 返回带UTC时区的datetime")

def test_ensure_aware_with_naive():
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    aware_dt = ensure_aware(naive_dt)
    assert aware_dt.tzinfo is not None
    assert aware_dt.tzinfo == timezone.utc
    print("✓ test_ensure_aware_with_naive: naive datetime成功转换为UTC aware")

def test_ensure_aware_with_aware():
    aware_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = ensure_aware(aware_dt)
    assert result.tzinfo == timezone.utc
    print("✓ test_ensure_aware_with_aware: aware datetime保持UTC不变")

def test_parse_iso_datetime_with_z():
    dt_str = "2024-01-15T08:30:00Z"
    dt = parse_iso_datetime(dt_str)
    assert dt.tzinfo is not None
    assert dt.utcoffset() == timedelta(0)
    print("✓ test_parse_iso_datetime_with_z: Z后缀ISO字符串解析正确")

def test_parse_iso_datetime_with_offset():
    dt_str = "2024-01-15T08:30:00+08:00"
    dt = parse_iso_datetime(dt_str)
    assert dt.tzinfo is not None
    assert dt.utcoffset() == timedelta(hours=8)
    print("✓ test_parse_iso_datetime_with_offset: 带时区偏移的ISO字符串解析正确")

def test_to_utc_with_naive():
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    utc_dt = to_utc(naive_dt)
    assert utc_dt.tzinfo == timezone.utc
    print("✓ test_to_utc_with_naive: naive datetime假设为UTC并转换")

def test_to_utc_with_aware():
    aware_dt = datetime(2024, 1, 1, 20, 0, 0, tzinfo=timezone(timedelta(hours=8)))
    utc_dt = to_utc(aware_dt)
    assert utc_dt.tzinfo == timezone.utc
    assert utc_dt.hour == 12
    print("✓ test_to_utc_with_aware: 带时区的datetime正确转换为UTC")

def test_parse_and_normalize_to_utc_string():
    time_value = "2024-01-15T08:30:00Z"
    result = parse_and_normalize_to_utc(time_value)
    assert result is not None
    assert result.tzinfo == timezone.utc
    print("✓ test_parse_and_normalize_to_utc_string: ISO字符串解析并转换为UTC")

def test_parse_and_normalize_to_utc_datetime_aware():
    time_value = datetime(2024, 1, 15, 16, 30, 0, tzinfo=timezone(timedelta(hours=8)))
    result = parse_and_normalize_to_utc(time_value)
    assert result is not None
    assert result.tzinfo == timezone.utc
    assert result.hour == 8
    print("✓ test_parse_and_normalize_to_utc_datetime_aware: aware datetime转换为UTC")

def test_parse_and_normalize_to_utc_datetime_naive():
    time_value = datetime(2024, 1, 15, 8, 30, 0)
    result = parse_and_normalize_to_utc(time_value)
    assert result is not None
    assert result.tzinfo == timezone.utc
    print("✓ test_parse_and_normalize_to_utc_datetime_naive: naive datetime假设为UTC")

def test_calculate_hours_between_aware_aware():
    start = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    hours = calculate_hours_between(start, end)
    assert hours == 4.0
    print("✓ test_calculate_hours_between_aware_aware: aware与aware时间差计算正确")

def test_calculate_hours_between_naive_aware():
    start = datetime(2024, 1, 15, 8, 0, 0)
    end = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    hours = calculate_hours_between(start, end)
    assert hours == 4.0
    print("✓ test_calculate_hours_between_naive_aware: naive与aware时间差计算正确（无TypeError）")

def test_calculate_hours_between_aware_naive():
    start = datetime(2024, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 12, 0, 0)
    hours = calculate_hours_between(start, end)
    assert hours == 4.0
    print("✓ test_calculate_hours_between_aware_naive: aware与naive时间差计算正确（无TypeError）")

def test_calculate_hours_between_string_input():
    start_str = "2024-01-15T08:00:00Z"
    end = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    hours = calculate_hours_between(parse_and_normalize_to_utc(start_str), end)
    assert hours == 4.0
    print("✓ test_calculate_hours_between_string_input: 字符串解析后时间差计算正确")

def test_format_iso_with_aware():
    dt = datetime(2024, 1, 15, 8, 30, 0, tzinfo=timezone.utc)
    formatted = format_iso(dt)
    assert formatted == "2024-01-15T08:30:00Z"
    print("✓ test_format_iso_with_aware: aware datetime格式化正确")

def test_format_iso_with_naive():
    dt = datetime(2024, 1, 15, 8, 30, 0)
    formatted = format_iso(dt)
    assert formatted == "2024-01-15T08:30:00Z"
    print("✓ test_format_iso_with_naive: naive datetime格式化正确")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("运行时间工具模块单元测试")
    print("="*60 + "\n")
    
    test_get_utc_now()
    test_ensure_aware_with_naive()
    test_ensure_aware_with_aware()
    test_parse_iso_datetime_with_z()
    test_parse_iso_datetime_with_offset()
    test_to_utc_with_naive()
    test_to_utc_with_aware()
    test_parse_and_normalize_to_utc_string()
    test_parse_and_normalize_to_utc_datetime_aware()
    test_parse_and_normalize_to_utc_datetime_naive()
    test_calculate_hours_between_aware_aware()
    test_calculate_hours_between_naive_aware()
    test_calculate_hours_between_aware_naive()
    test_calculate_hours_between_string_input()
    test_format_iso_with_aware()
    test_format_iso_with_naive()
    
    print("\n" + "="*60)
    print("所有测试通过！")
    print("="*60 + "\n")