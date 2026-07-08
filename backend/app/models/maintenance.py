from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MaintenanceCycle(BaseModel):
    cycle_name: str = Field(..., description="周期名称")
    equipment_code: str = Field(..., description="设备编号")
    cycle_type: str = Field(..., description="周期类型: 每日/每周/每月/每季度/每年")
    interval_days: int = Field(..., description="间隔天数")
    reminder_days: int = Field(7, description="提前提醒天数")
    status: str = Field("启用", description="状态: 启用/停用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class MaintenancePlan(BaseModel):
    plan_name: str = Field(..., description="计划名称")
    equipment_codes: List[str] = Field(..., description="关联设备编号列表")
    cycle_type: str = Field(..., description="周期类型")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    assignee: str = Field(..., description="负责人")
    status: str = Field("待执行", description="状态: 待执行/执行中/已完成/已取消")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class MaintenanceTask(BaseModel):
    plan_id: str = Field(..., description="关联计划ID")
    equipment_code: str = Field(..., description="设备编号")
    scheduled_date: datetime = Field(..., description="计划执行日期")
    assignee: str = Field(..., description="执行人")
    status: str = Field("待执行", description="状态: 待执行/已完成/逾期")
    actual_date: Optional[datetime] = Field(None, description="实际执行日期")
    maintenance_result: Optional[str] = Field(None, description="维保结果")
    remarks: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class MaintenanceRecord(BaseModel):
    equipment_code: str = Field(..., description="设备编号")
    equipment_name: str = Field(..., description="设备名称")
    maintainer: str = Field(..., description="维保人员")
    maintenance_date: datetime = Field(..., description="维保日期")
    maintenance_type: str = Field(..., description="维保类型: 日常保养/定期维护/专项检修")
    items: List[dict] = Field(..., description="维保项目")
    overall_status: str = Field(..., description="总体状态: 正常/异常")
    remarks: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

class MaintenanceReminder(BaseModel):
    equipment_code: str = Field(..., description="设备编号")
    equipment_name: str = Field(..., description="设备名称")
    due_date: datetime = Field(..., description="到期日期")
    days_remaining: int = Field(..., description="剩余天数")
    assignee: str = Field(..., description="负责人")
    reminder_status: str = Field("未处理", description="提醒状态: 未处理/已处理/已过期")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")