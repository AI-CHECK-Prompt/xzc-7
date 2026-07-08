from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class InspectionPlan(BaseModel):
    plan_name: str = Field(..., description="计划名称")
    equipment_codes: List[str] = Field(..., description="关联设备编号列表")
    frequency: str = Field(..., description="巡检频率: 每日/每周/每月/每季度/每年")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    assignee: str = Field(..., description="负责人")
    status: str = Field("待执行", description="计划状态: 待执行/执行中/已完成/已取消")
    
class InspectionTask(BaseModel):
    plan_id: str = Field(..., description="关联计划ID")
    equipment_code: str = Field(..., description="设备编号")
    scheduled_date: datetime = Field(..., description="计划执行日期")
    assignee: str = Field(..., description="执行人")
    status: str = Field("待执行", description="任务状态: 待执行/已完成/逾期")
    actual_date: Optional[datetime] = Field(None, description="实际执行日期")
    inspection_result: Optional[str] = Field(None, description="巡检结果")
    issues_found: Optional[str] = Field(None, description="发现问题")
    
class InspectionRecord(BaseModel):
    equipment_code: str = Field(..., description="设备编号")
    inspector: str = Field(..., description="巡检人员")
    inspection_date: datetime = Field(..., description="巡检日期")
    items: List[dict] = Field(..., description="巡检项目")
    overall_status: str = Field(..., description="总体状态: 正常/异常")
    remarks: Optional[str] = Field(None, description="备注")

FREQUENCY_OPTIONS = ["每日", "每周", "每月", "每季度", "每年"]
PLAN_STATUS_OPTIONS = ["待执行", "执行中", "已完成", "已取消"]
TASK_STATUS_OPTIONS = ["待执行", "已完成", "逾期"]

class InspectionPlanUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, description="计划名称")
    equipment_codes: Optional[List[str]] = Field(None, description="关联设备编号列表")
    frequency: Optional[str] = Field(None, description="巡检频率")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    assignee: Optional[str] = Field(None, description="负责人")
    status: Optional[str] = Field(None, description="计划状态")

    @field_validator('frequency')
    def validate_frequency(cls, v):
        if v is not None and v not in FREQUENCY_OPTIONS:
            raise ValueError(f"巡检频率必须是: {', '.join(FREQUENCY_OPTIONS)}")
        return v

    @field_validator('status')
    def validate_plan_status(cls, v):
        if v is not None and v not in PLAN_STATUS_OPTIONS:
            raise ValueError(f"计划状态必须是: {', '.join(PLAN_STATUS_OPTIONS)}")
        return v

    @field_validator('plan_name', 'assignee')
    def validate_non_empty_string(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("不能为空字符串")
        return v

    @field_validator('equipment_codes')
    def validate_equipment_codes(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("设备编号列表不能为空")
        return v

    @field_validator('end_date')
    def validate_date_order(cls, v, values):
        if v is not None and 'start_date' in values.data and values.data['start_date'] is not None:
            start_date = values.data['start_date']
            if v <= start_date:
                raise ValueError("结束日期必须晚于开始日期")
        return v

class InspectionTaskUpdate(BaseModel):
    plan_id: Optional[str] = Field(None, description="关联计划ID")
    equipment_code: Optional[str] = Field(None, description="设备编号")
    scheduled_date: Optional[datetime] = Field(None, description="计划执行日期")
    assignee: Optional[str] = Field(None, description="执行人")
    status: Optional[str] = Field(None, description="任务状态")
    actual_date: Optional[datetime] = Field(None, description="实际执行日期")
    inspection_result: Optional[str] = Field(None, description="巡检结果")
    issues_found: Optional[str] = Field(None, description="发现问题")

    @field_validator('status')
    def validate_task_status(cls, v):
        if v is not None and v not in TASK_STATUS_OPTIONS:
            raise ValueError(f"任务状态必须是: {', '.join(TASK_STATUS_OPTIONS)}")
        return v

    @field_validator('plan_id', 'equipment_code', 'assignee')
    def validate_non_empty_string(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("不能为空字符串")
        return v
