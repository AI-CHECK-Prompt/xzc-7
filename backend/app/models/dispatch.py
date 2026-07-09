from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime

class SkillTag(BaseModel):
    equipment_type: str = Field(..., description="设备类型")
    professional_field: str = Field(..., description="专业领域")
    skill_level: str = Field(..., description="技能等级: 初级/中级/高级/专家")

class Staff(BaseModel):
    staff_id: str = Field(..., description="人员ID")
    name: str = Field(..., description="人员姓名")
    skill_tags: List[SkillTag] = Field([], description="技能标签列表")
    real_time_location: Dict[str, float] = Field(..., description="实时位置: {longitude, latitude}")
    current_task_count: int = Field(0, description="当前任务负载")
    max_task_limit: int = Field(5, description="最大任务上限")
    shift_status: str = Field("在岗", description="值班状态: 在岗/休息/请假/离线/交接班")
    work_start_time: Optional[datetime] = Field(None, description="连续工作开始时间")
    max_continuous_work_hours: float = Field(8.0, description="最大连续工作时长(小时)")
    department: str = Field(..., description="所属科室")
    status: str = Field("active", description="人员状态: active/inactive")
    
    @field_validator('shift_status')
    def validate_shift_status(cls, v):
        valid_status = ["在岗", "休息", "请假", "离线", "交接班"]
        if v not in valid_status:
            raise ValueError(f"值班状态必须是: {', '.join(valid_status)}")
        return v

    @field_validator('skill_level', check_fields=False)
    def validate_skill_level(cls, v):
        valid_levels = ["初级", "中级", "高级", "专家"]
        if v not in valid_levels:
            raise ValueError(f"技能等级必须是: {', '.join(valid_levels)}")
        return v

class StaffUpdate(BaseModel):
    name: Optional[str] = Field(None, description="人员姓名")
    skill_tags: Optional[List[SkillTag]] = Field(None, description="技能标签列表")
    real_time_location: Optional[Dict[str, float]] = Field(None, description="实时位置")
    current_task_count: Optional[int] = Field(None, description="当前任务负载")
    max_task_limit: Optional[int] = Field(None, description="最大任务上限")
    shift_status: Optional[str] = Field(None, description="值班状态")
    work_start_time: Optional[datetime] = Field(None, description="连续工作开始时间")
    max_continuous_work_hours: Optional[float] = Field(None, description="最大连续工作时长")
    department: Optional[str] = Field(None, description="所属科室")
    status: Optional[str] = Field(None, description="人员状态")

class MatchingStrategy(BaseModel):
    strategy_name: str = Field(..., description="策略名称")
    equipment_type: Optional[str] = Field(None, description="设备类型")
    required_fields: List[str] = Field([], description="必需匹配字段")
    optional_fields: List[str] = Field([], description="可选匹配字段")
    min_skill_level: str = Field("初级", description="最低技能等级要求")

class ScoringWeight(BaseModel):
    skill_match_weight: float = Field(0.35, description="技能匹配度权重")
    location_weight: float = Field(0.25, description="位置权重")
    arrival_time_weight: float = Field(0.15, description="预计到达时间权重")
    load_weight: float = Field(0.15, description="任务负载权重")
    work_duration_weight: float = Field(0.10, description="连续工作时长权重")

class EscalationRule(BaseModel):
    level: int = Field(1, description="升级级别")
    description: str = Field(..., description="升级描述")
    reduce_skill_level: bool = Field(False, description="是否降低技能等级要求")
    expand_distance_radius: Optional[float] = Field(None, description="扩大距离半径(公里)")
    notify_admin: bool = Field(False, description="是否通知管理员")

class DispatchConfig(BaseModel):
    config_name: str = Field(..., description="配置名称")
    is_active: bool = Field(True, description="是否启用")
    matching_strategies: List[MatchingStrategy] = Field([], description="匹配策略列表")
    scoring_weights: ScoringWeight = Field(..., description="评分权重配置")
    escalation_rules: List[EscalationRule] = Field([], description="升级规则列表")
    max_dispatch_retries: int = Field(3, description="最大派单重试次数")
    dispatch_timeout_seconds: int = Field(300, description="派单超时时间(秒)")
    max_distance_km: float = Field(5.0, description="最大距离限制(公里)")
    auto_redispatch_enabled: bool = Field(True, description="是否启用自动重新派单")
    manual_dispatch_lock: bool = Field(True, description="人工派单后是否锁定自动派单")

class DispatchConfigUpdate(BaseModel):
    config_name: Optional[str] = Field(None, description="配置名称")
    is_active: Optional[bool] = Field(None, description="是否启用")
    matching_strategies: Optional[List[MatchingStrategy]] = Field(None, description="匹配策略列表")
    scoring_weights: Optional[ScoringWeight] = Field(None, description="评分权重配置")
    escalation_rules: Optional[List[EscalationRule]] = Field(None, description="升级规则列表")
    max_dispatch_retries: Optional[int] = Field(None, description="最大派单重试次数")
    dispatch_timeout_seconds: Optional[int] = Field(None, description="派单超时时间")
    max_distance_km: Optional[float] = Field(None, description="最大距离限制")
    auto_redispatch_enabled: Optional[bool] = Field(None, description="是否启用自动重新派单")
    manual_dispatch_lock: Optional[bool] = Field(None, description="人工派单后是否锁定自动派单")

class CandidateScore(BaseModel):
    staff_id: str = Field(..., description="人员ID")
    staff_name: str = Field(..., description="人员姓名")
    skill_match_score: float = Field(0.0, description="技能匹配度分数")
    location_score: float = Field(0.0, description="位置分数")
    arrival_time_score: float = Field(0.0, description="预计到达时间分数")
    load_score: float = Field(0.0, description="任务负载分数")
    work_duration_score: float = Field(0.0, description="连续工作时长分数")
    total_score: float = Field(0.0, description="综合评分")
    distance_km: float = Field(0.0, description="距离(公里)")
    estimated_arrival_minutes: float = Field(0.0, description="预计到达时间(分钟)")
    current_load: int = Field(0, description="当前任务负载")
    continuous_work_hours: float = Field(0.0, description="连续工作时长(小时)")

class ManualAdjustment(BaseModel):
    operator_id: str = Field(..., description="操作人ID")
    operator_name: str = Field(..., description="操作人姓名")
    adjustment_reason: str = Field(..., description="调整原因")
    previous_assignee: Optional[str] = Field(None, description="调整前派单对象")
    new_assignee: str = Field(..., description="调整后派单对象")
    adjustment_time: datetime = Field(default_factory=datetime.now, description="调整时间")

class DispatchHistory(BaseModel):
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field("inspection", description="任务类型")
    equipment_code: str = Field(..., description="设备编号")
    candidates: List[CandidateScore] = Field([], description="候选人员列表及评分")
    selected_staff_id: Optional[str] = Field(None, description="选中人员ID")
    selected_staff_name: Optional[str] = Field(None, description="选中人员姓名")
    dispatch_method: str = Field("auto", description="派单方式: auto/manual")
    dispatch_reason: str = Field("", description="派单原因")
    dispatch_time: datetime = Field(default_factory=datetime.now, description="派单时间")
    dispatch_duration_ms: float = Field(0.0, description="派单耗时(毫秒)")
    escalation_level: int = Field(0, description="使用的升级级别")
    manual_adjustment: Optional[ManualAdjustment] = Field(None, description="人工调整信息")
    is_redispatch: bool = Field(False, description="是否为重新派单")
    previous_dispatch_id: Optional[str] = Field(None, description="上一次派单记录ID")
    status: str = Field("success", description="派单状态: success/failed/pending")

class DispatchLock(BaseModel):
    task_id: str = Field(..., description="任务ID")
    lock_owner: str = Field(..., description="锁持有者")
    lock_time: datetime = Field(default_factory=datetime.now, description="加锁时间")
    expires_at: datetime = Field(..., description="过期时间")
    is_active: bool = Field(True, description="是否有效")