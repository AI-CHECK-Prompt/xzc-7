from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Equipment(BaseModel):
    equipment_code: str = Field(..., description="设备编号")
    name: str = Field(..., description="设备名称")
    model: str = Field(..., description="设备型号")
    manufacturer: str = Field(..., description="生产厂家")
    department: str = Field(..., description="所属科室")
    location: str = Field(..., description="安装位置")
    purchase_date: datetime = Field(..., description="采购日期")
    warranty_period: Optional[int] = Field(None, description="保修期(月)")
    status: str = Field("正常", description="设备状态: 正常/故障/维修中/停用")
    
class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    warranty_period: Optional[int] = None
    status: Optional[str] = None
