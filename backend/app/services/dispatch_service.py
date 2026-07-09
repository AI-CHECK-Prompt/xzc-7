from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from bson import ObjectId
import logging
import time

from app.database import (
    staff_collection,
    dispatch_config_collection,
    dispatch_history_collection,
    dispatch_lock_collection,
    inspection_collection,
    equipment_collection
)
from app.models.dispatch import (
    Staff,
    DispatchConfig,
    CandidateScore,
    DispatchHistory,
    DispatchLock,
    MatchingStrategy,
    EscalationRule,
    ScoringWeight
)

logger = logging.getLogger(__name__)

SKILL_LEVEL_ORDER = {"初级": 1, "中级": 2, "高级": 3, "专家": 4}

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def get_current_config() -> Optional[DispatchConfig]:
    config = dispatch_config_collection.find_one({"is_active": True})
    if config:
        return DispatchConfig(**config)
    default_config = DispatchConfig(
        config_name="默认派单配置",
        is_active=True,
        matching_strategies=[
            MatchingStrategy(
                strategy_name="通用策略",
                min_skill_level="初级",
                required_fields=["equipment_type"],
                optional_fields=["professional_field"]
            )
        ],
        scoring_weights=ScoringWeight(
            skill_match_weight=0.35,
            location_weight=0.25,
            arrival_time_weight=0.15,
            load_weight=0.15,
            work_duration_weight=0.10
        ),
        escalation_rules=[
            EscalationRule(level=1, description="降低技能等级要求", reduce_skill_level=True),
            EscalationRule(level=2, description="扩大距离范围", expand_distance_radius=10.0),
            EscalationRule(level=3, description="通知管理员人工介入", notify_admin=True)
        ]
    )
    dispatch_config_collection.insert_one(default_config.model_dump())
    return default_config

def acquire_dispatch_lock(task_id: str, lock_owner: str, timeout_seconds: int = 300) -> bool:
    try:
        now = datetime.now()
        expires_at = now + timedelta(seconds=timeout_seconds)
        
        expired_locks = dispatch_lock_collection.delete_many({
            "task_id": task_id,
            "expires_at": {"$lt": now},
            "is_active": True
        })
        if expired_locks.deleted_count > 0:
            logger.info(f"清理过期锁: task_id={task_id}, 清理数量={expired_locks.deleted_count}")
        
        lock_doc = {
            "task_id": task_id,
            "lock_owner": lock_owner,
            "lock_time": now,
            "expires_at": expires_at,
            "is_active": True
        }
        
        result = dispatch_lock_collection.insert_one(lock_doc)
        return result.inserted_id is not None
    except Exception as e:
        if "duplicate key" in str(e):
            return False
        logger.error(f"获取派单锁失败: {e}")
        return False

def release_dispatch_lock(task_id: str):
    dispatch_lock_collection.update_one(
        {"task_id": task_id, "is_active": True},
        {"$set": {"is_active": False}}
    )

def is_staff_available(staff: dict, config: DispatchConfig) -> bool:
    if staff.get("status") != "active":
        return False
    
    shift_status = staff.get("shift_status", "在岗")
    unavailable_status = ["请假", "离线", "交接班"]
    if shift_status in unavailable_status:
        return False
    
    current_task_count = staff.get("current_task_count", 0)
    max_task_limit = staff.get("max_task_limit", 5)
    if current_task_count >= max_task_limit:
        return False
    
    work_start_time = staff.get("work_start_time")
    if work_start_time:
        max_continuous = staff.get("max_continuous_work_hours", 8.0)
        if isinstance(work_start_time, str):
            work_start_time = datetime.fromisoformat(work_start_time.replace("Z", "+00:00"))
        continuous_hours = (datetime.now() - work_start_time).total_seconds() / 3600
        if continuous_hours >= max_continuous:
            return False
    
    return True

def get_equipment_location(equipment_code: str) -> Optional[Dict[str, float]]:
    equipment = equipment_collection.find_one({"equipment_code": equipment_code})
    if equipment and equipment.get("location"):
        return {"latitude": 30.5728, "longitude": 104.0668}
    return {"latitude": 30.5728, "longitude": 104.0668}

def calculate_skill_match(staff: dict, equipment_type: str, 
                          strategy: MatchingStrategy, escalation_level: int = 0) -> float:
    skill_tags = staff.get("skill_tags", [])
    matched_count = 0
    total_required = len(strategy.required_fields)
    total_optional = len(strategy.optional_fields)
    
    min_skill_level = strategy.min_skill_level
    if escalation_level > 0:
        level_index = max(0, SKILL_LEVEL_ORDER.get(min_skill_level, 1) - escalation_level)
        min_skill_level = next(k for k, v in SKILL_LEVEL_ORDER.items() if v == level_index)
    
    for tag in skill_tags:
        if tag.get("equipment_type") == equipment_type:
            if "equipment_type" in strategy.required_fields:
                matched_count += 1
            
            skill_level = tag.get("skill_level", "初级")
            level_score = SKILL_LEVEL_ORDER.get(skill_level, 1) / SKILL_LEVEL_ORDER.get(min_skill_level, 1)
            level_score = min(level_score, 1.0)
            
            if "professional_field" in strategy.required_fields or "professional_field" in strategy.optional_fields:
                matched_count += 0.5 * level_score
    
    total_fields = total_required + total_optional * 0.5
    if total_fields == 0:
        return 0.5
    
    return min(matched_count / total_fields, 1.0)

def calculate_location_score(distance_km: float, max_distance: float) -> float:
    if distance_km <= 0:
        return 1.0
    if distance_km >= max_distance:
        return 0.0
    return 1.0 - (distance_km / max_distance)

def calculate_arrival_time_score(estimated_minutes: float) -> float:
    if estimated_minutes <= 0:
        return 1.0
    if estimated_minutes >= 60:
        return 0.0
    return 1.0 - (estimated_minutes / 60)

def calculate_load_score(current_load: int, max_load: int) -> float:
    if max_load <= 0:
        return 1.0
    return 1.0 - (current_load / max_load)

def calculate_work_duration_score(continuous_hours: float, max_hours: float) -> float:
    if continuous_hours <= 0:
        return 1.0
    if continuous_hours >= max_hours:
        return 0.0
    return 1.0 - (continuous_hours / max_hours)

def filter_candidates(equipment_code: str, config: DispatchConfig, 
                      escalation_level: int = 0) -> List[dict]:
    equipment = equipment_collection.find_one({"equipment_code": equipment_code})
    if not equipment:
        return []
    
    equipment_type = equipment.get("model", "通用")
    
    max_distance = config.max_distance_km
    if escalation_level > 0:
        for rule in config.escalation_rules:
            if rule.level == escalation_level and rule.expand_distance_radius:
                max_distance = rule.expand_distance_radius
                break
    
    equipment_location = get_equipment_location(equipment_code)
    
    department = equipment.get("department")
    query = {"status": "active"}
    if department:
        query["department"] = department
    
    all_staff = list(staff_collection.find(query))
    candidates = []
    
    for staff in all_staff:
        if not is_staff_available(staff, config):
            continue
        
        staff_location = staff.get("real_time_location", {"latitude": 0, "longitude": 0})
        distance = calculate_distance(
            equipment_location["latitude"],
            equipment_location["longitude"],
            staff_location.get("latitude", 0),
            staff_location.get("longitude", 0)
        )
        
        if distance > max_distance:
            continue
        
        matched_strategy = None
        for strategy in config.matching_strategies:
            if strategy.equipment_type is None or strategy.equipment_type == equipment_type:
                matched_strategy = strategy
                break
        
        if matched_strategy is None:
            matched_strategy = config.matching_strategies[0] if config.matching_strategies else None
        
        if matched_strategy:
            skill_score = calculate_skill_match(staff, equipment_type, matched_strategy, escalation_level)
            if skill_score > 0:
                candidates.append({
                    "staff": staff,
                    "distance": distance,
                    "skill_score": skill_score
                })
    
    return candidates

def score_candidates(candidates: List[dict], config: DispatchConfig, 
                     equipment_location: Dict[str, float],
                     max_distance: Optional[float] = None) -> List[CandidateScore]:
    scores = []
    weights = config.scoring_weights
    
    for candidate in candidates:
        staff = candidate["staff"]
        distance = candidate["distance"]
        skill_score = candidate["skill_score"]
        
        location_score = calculate_location_score(distance, max_distance or config.max_distance_km)
        
        speed_kmh = 30.0
        estimated_arrival_minutes = (distance / speed_kmh) * 60 if speed_kmh > 0 else 60
        arrival_time_score = calculate_arrival_time_score(estimated_arrival_minutes)
        
        current_load = staff.get("current_task_count", 0)
        max_load = staff.get("max_task_limit", 5)
        load_score = calculate_load_score(current_load, max_load)
        
        work_start_time = staff.get("work_start_time")
        if work_start_time:
            if isinstance(work_start_time, str):
                work_start_time = datetime.fromisoformat(work_start_time.replace("Z", "+00:00"))
            continuous_hours = (datetime.now() - work_start_time).total_seconds() / 3600
        else:
            continuous_hours = 0
        max_hours = staff.get("max_continuous_work_hours", 8.0)
        work_duration_score = calculate_work_duration_score(continuous_hours, max_hours)
        
        total_score = (
            skill_score * weights.skill_match_weight +
            location_score * weights.location_weight +
            arrival_time_score * weights.arrival_time_weight +
            load_score * weights.load_weight +
            work_duration_score * weights.work_duration_weight
        )
        
        candidate_score = CandidateScore(
            staff_id=staff["staff_id"],
            staff_name=staff["name"],
            skill_match_score=round(skill_score, 4),
            location_score=round(location_score, 4),
            arrival_time_score=round(arrival_time_score, 4),
            load_score=round(load_score, 4),
            work_duration_score=round(work_duration_score, 4),
            total_score=round(total_score, 4),
            distance_km=round(distance, 4),
            estimated_arrival_minutes=round(estimated_arrival_minutes, 2),
            current_load=current_load,
            continuous_work_hours=round(continuous_hours, 2)
        )
        scores.append(candidate_score)
    
    scores.sort(key=lambda x: x.total_score, reverse=True)
    return scores

def select_best_candidate(scores: List[CandidateScore], config: DispatchConfig) -> Optional[CandidateScore]:
    if not scores:
        return None
    
    for score in scores:
        result = staff_collection.update_one(
            {
                "staff_id": score.staff_id,
                "current_task_count": {"$lt": score.current_load + 1},
                "max_task_limit": {"$gt": score.current_load}
            },
            {"$inc": {"current_task_count": 1}}
        )
        if result.modified_count > 0:
            return score
    
    return None

def log_dispatch_history(task_id: str, equipment_code: str, task_type: str,
                         candidates: List[CandidateScore], selected_staff: Optional[CandidateScore],
                         dispatch_method: str, dispatch_reason: str, 
                         dispatch_duration_ms: float, escalation_level: int = 0,
                         is_redispatch: bool = False, previous_dispatch_id: Optional[str] = None,
                         manual_adjustment: Optional[dict] = None) -> str:
    history = DispatchHistory(
        task_id=task_id,
        task_type=task_type,
        equipment_code=equipment_code,
        candidates=[c.dict() for c in candidates],
        selected_staff_id=selected_staff.staff_id if selected_staff else None,
        selected_staff_name=selected_staff.staff_name if selected_staff else None,
        dispatch_method=dispatch_method,
        dispatch_reason=dispatch_reason,
        dispatch_duration_ms=dispatch_duration_ms,
        escalation_level=escalation_level,
        is_redispatch=is_redispatch,
        previous_dispatch_id=previous_dispatch_id,
        status="success" if selected_staff else "failed",
        manual_adjustment=manual_adjustment
    )
    
    result = dispatch_history_collection.insert_one(history.dict())
    return str(result.inserted_id)

def execute_dispatch(task_id: str, equipment_code: str, 
                     task_type: str = "inspection",
                     is_redispatch: bool = False,
                     previous_dispatch_id: Optional[str] = None) -> Dict[str, any]:
    start_time = time.time()
    
    config = get_current_config()
    if not config:
        return {"success": False, "error": "未找到派单配置"}
    
    if not acquire_dispatch_lock(task_id, f"dispatch_{task_id}"):
        return {"success": False, "error": "任务正在派单中"}
    
    try:
        task = inspection_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        if task.get("manual_dispatch_locked", False):
            return {"success": False, "error": "任务已被人工派单锁定"}
        
        final_candidates = []
        final_scores = []
        selected_staff = None
        escalation_level = 0
        dispatch_reason = ""
        
        for level in range(config.max_dispatch_retries + 1):
            candidates = filter_candidates(equipment_code, config, level)
            if not candidates:
                escalation_level = level
                continue
            
            equipment_location = get_equipment_location(equipment_code)
            
            max_distance = config.max_distance_km
            if level > 0:
                for rule in config.escalation_rules:
                    if rule.level == level and rule.expand_distance_radius:
                        max_distance = rule.expand_distance_radius
                        break
            
            scores = score_candidates(candidates, config, equipment_location, max_distance)
            final_candidates.extend(candidates)
            final_scores = scores
            
            selected = select_best_candidate(scores, config)
            if selected:
                selected_staff = selected
                escalation_level = level
                break
        
        if selected_staff:
            result = inspection_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {
                    "assignee": selected_staff.staff_id,
                    "assignee_name": selected_staff.staff_name,
                    "dispatch_status": "已派单",
                    "dispatch_time": datetime.now()
                }}
            )
            dispatch_reason = f"自动派单成功，综合评分: {selected_staff.total_score:.4f}"
        else:
            dispatch_reason = f"自动派单失败，已尝试{config.max_dispatch_retries}次升级"
            
            for rule in config.escalation_rules:
                if rule.level == escalation_level and rule.notify_admin:
                    logger.warning(f"派单失败，通知管理员介入: task_id={task_id}, equipment_code={equipment_code}")
                    break
        
        duration_ms = (time.time() - start_time) * 1000
        
        history_id = log_dispatch_history(
            task_id=task_id,
            equipment_code=equipment_code,
            task_type=task_type,
            candidates=final_scores,
            selected_staff=selected_staff,
            dispatch_method="auto",
            dispatch_reason=dispatch_reason,
            dispatch_duration_ms=round(duration_ms, 2),
            escalation_level=escalation_level,
            is_redispatch=is_redispatch,
            previous_dispatch_id=previous_dispatch_id
        )
        
        return {
            "success": selected_staff is not None,
            "task_id": task_id,
            "selected_staff_id": selected_staff.staff_id if selected_staff else None,
            "selected_staff_name": selected_staff.staff_name if selected_staff else None,
            "candidates_count": len(final_scores),
            "escalation_level": escalation_level,
            "dispatch_duration_ms": round(duration_ms, 2),
            "history_id": history_id,
            "message": dispatch_reason
        }
    
    finally:
        release_dispatch_lock(task_id)

def manual_dispatch(task_id: str, equipment_code: str, 
                    staff_id: str, operator_id: str, 
                    operator_name: str, reason: str) -> Dict[str, any]:
    start_time = time.time()
    
    config = get_current_config()
    if not config:
        return {"success": False, "error": "未找到派单配置"}
    
    if not acquire_dispatch_lock(task_id, f"manual_{operator_id}"):
        return {"success": False, "error": "任务正在派单中"}
    
    try:
        task = inspection_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        staff = staff_collection.find_one({"staff_id": staff_id})
        if not staff:
            return {"success": False, "error": "人员不存在"}
        
        if not is_staff_available(staff, config):
            return {"success": False, "error": "人员当前不可派单"}
        
        previous_assignee = task.get("assignee")
        
        staff_collection.update_one(
            {"staff_id": staff_id},
            {"$inc": {"current_task_count": 1}}
        )
        
        update_data = {
            "assignee": staff_id,
            "assignee_name": staff["name"],
            "dispatch_status": "人工派单",
            "dispatch_time": datetime.now(),
            "manual_dispatch_locked": config.manual_dispatch_lock
        }
        
        if previous_assignee and previous_assignee != staff_id:
            staff_collection.update_one(
                {"staff_id": previous_assignee},
                {"$inc": {"current_task_count": -1}}
            )
        
        inspection_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        manual_adjustment = {
            "operator_id": operator_id,
            "operator_name": operator_name,
            "adjustment_reason": reason,
            "previous_assignee": previous_assignee,
            "new_assignee": staff_id,
            "adjustment_time": datetime.now()
        }
        
        duration_ms = (time.time() - start_time) * 1000
        
        history_id = log_dispatch_history(
            task_id=task_id,
            equipment_code=equipment_code,
            task_type="inspection",
            candidates=[],
            selected_staff=None,
            dispatch_method="manual",
            dispatch_reason=f"人工派单: {reason}",
            dispatch_duration_ms=round(duration_ms, 2),
            manual_adjustment=manual_adjustment
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "selected_staff_id": staff_id,
            "selected_staff_name": staff["name"],
            "history_id": history_id,
            "message": f"人工派单成功，已分配给 {staff['name']}"
        }
    
    finally:
        release_dispatch_lock(task_id)

def re_dispatch(task_id: str) -> Dict[str, any]:
    task = inspection_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        return {"success": False, "error": "任务不存在"}
    
    if task.get("status") == "已完成":
        return {"success": False, "error": "任务已完成，无法重新派单"}
    
    equipment_code = task.get("equipment_code")
    if not equipment_code:
        return {"success": False, "error": "任务未关联设备"}
    
    previous_dispatch_id = None
    last_history = dispatch_history_collection.find_one(
        {"task_id": task_id},
        sort=[("dispatch_time", -1)]
    )
    if last_history:
        previous_dispatch_id = str(last_history["_id"])
    
    previous_assignee = task.get("assignee")
    if previous_assignee:
        staff_collection.update_one(
            {"staff_id": previous_assignee},
            {"$inc": {"current_task_count": -1}}
        )
    
    result = execute_dispatch(task_id, equipment_code, is_redispatch=True, previous_dispatch_id=previous_dispatch_id)
    
    return result

def unlock_manual_dispatch(task_id: str) -> bool:
    result = inspection_collection.update_one(
        {"_id": ObjectId(task_id), "manual_dispatch_locked": True},
        {"$set": {"manual_dispatch_locked": False}}
    )
    return result.modified_count > 0

def get_dispatch_statistics(start_time: Optional[datetime] = None, 
                            end_time: Optional[datetime] = None,
                            equipment_type: Optional[str] = None,
                            department: Optional[str] = None) -> Dict[str, any]:
    query = {}
    
    if start_time:
        query["dispatch_time"] = {"$gte": start_time}
    if end_time:
        if "dispatch_time" in query:
            query["dispatch_time"]["$lte"] = end_time
        else:
            query["dispatch_time"] = {"$lte": end_time}
    
    total_count = dispatch_history_collection.count_documents(query)
    
    success_count = dispatch_history_collection.count_documents({
        **query,
        "status": "success"
    })
    
    auto_count = dispatch_history_collection.count_documents({
        **query,
        "dispatch_method": "auto"
    })
    
    manual_count = dispatch_history_collection.count_documents({
        **query,
        "dispatch_method": "manual"
    })
    
    redispatch_count = dispatch_history_collection.count_documents({
        **query,
        "is_redispatch": True
    })
    
    avg_duration = dispatch_history_collection.aggregate([
        {"$match": query},
        {"$group": {"_id": None, "avg": {"$avg": "$dispatch_duration_ms"}}}
    ])
    
    avg_duration_ms = 0
    for doc in avg_duration:
        avg_duration_ms = doc.get("avg", 0)
    
    total_candidates = dispatch_history_collection.aggregate([
        {"$match": query},
        {"$project": {"count": {"$size": "$candidates"}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ])
    
    avg_candidates = 0
    for doc in total_candidates:
        total = doc.get("total", 0)
        avg_candidates = total / total_count if total_count > 0 else 0
    
    staff_utilization = {}
    if auto_count > 0:
        staff_stats = dispatch_history_collection.aggregate([
            {"$match": {**query, "dispatch_method": "auto", "status": "success"}},
            {"$group": {"_id": "$selected_staff_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        for stat in staff_stats:
            staff_id = stat["_id"]
            if staff_id:
                staff = staff_collection.find_one({"staff_id": staff_id})
                staff_utilization[staff_id] = {
                    "name": staff["name"] if staff else staff_id,
                    "task_count": stat["count"]
                }
    
    return {
        "total_dispatch": total_count,
        "success_dispatch": success_count,
        "failed_dispatch": total_count - success_count,
        "success_rate": round(success_count / total_count * 100, 2) if total_count > 0 else 0,
        "auto_dispatch": auto_count,
        "manual_dispatch": manual_count,
        "manual_intervention_rate": round(manual_count / total_count * 100, 2) if total_count > 0 else 0,
        "redispatch_count": redispatch_count,
        "redispatch_rate": round(redispatch_count / total_count * 100, 2) if total_count > 0 else 0,
        "avg_dispatch_duration_ms": round(avg_duration_ms, 2),
        "avg_candidates_per_dispatch": round(avg_candidates, 2),
        "staff_utilization": staff_utilization
    }

def get_dispatch_history(task_id: Optional[str] = None, 
                         staff_id: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         page: int = 1, page_size: int = 10) -> Dict[str, any]:
    query = {}
    
    if task_id:
        query["task_id"] = task_id
    if staff_id:
        query["selected_staff_id"] = staff_id
    if start_time:
        query["dispatch_time"] = {"$gte": start_time}
    if end_time:
        if "dispatch_time" in query:
            query["dispatch_time"]["$lte"] = end_time
        else:
            query["dispatch_time"] = {"$lte": end_time}
    
    skip = (page - 1) * page_size
    total = dispatch_history_collection.count_documents(query)
    histories = list(dispatch_history_collection.find(query)
                     .sort("dispatch_time", -1)
                     .skip(skip)
                     .limit(page_size))
    
    for history in histories:
        history["_id"] = str(history["_id"])
        if isinstance(history.get("dispatch_time"), datetime):
            history["dispatch_time"] = history["dispatch_time"].isoformat()
        if history.get("manual_adjustment"):
            if isinstance(history["manual_adjustment"].get("adjustment_time"), datetime):
                history["manual_adjustment"]["adjustment_time"] = history["manual_adjustment"]["adjustment_time"].isoformat()
    
    return {"data": histories, "total": total, "page": page, "page_size": page_size}