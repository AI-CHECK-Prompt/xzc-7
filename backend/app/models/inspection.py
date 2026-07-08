from pydantic import BaseModel, Field
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
