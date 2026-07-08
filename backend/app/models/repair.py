from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RepairOrder(BaseModel):
    equipment_code: str = Field(..., description="设备编号")
    equipment_name: str = Field(..., description="设备名称")
    reporter: str = Field(..., description="报修人")
    department: str = Field(..., description="报修科室")
    description: str = Field(..., description="故障描述")
    priority: str = Field("一般", description="优先级: 紧急/重要/一般")
    status: str = Field("待处理", description="状态: 待处理/已接单/维修中/已完成/已取消")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
class RepairUpdate(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    repair_date: Optional[datetime] = None
    repair_result: Optional[str] = None
    remarks: Optional[str] = None
