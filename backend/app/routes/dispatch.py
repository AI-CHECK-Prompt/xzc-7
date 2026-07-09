from fastapi import APIRouter, HTTPException
from app.database import dispatch_config_collection
from app.models.dispatch import DispatchConfig, DispatchConfigUpdate
from app.services.dispatch_service import (
    execute_dispatch,
    manual_dispatch,
    re_dispatch,
    unlock_manual_dispatch,
    get_dispatch_statistics,
    get_dispatch_history
)
from bson import ObjectId
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.post("/config", response_description="创建派单配置")
async def create_dispatch_config(config: DispatchConfig):
    try:
        existing = dispatch_config_collection.find_one({"config_name": config.config_name})
        if existing:
            raise HTTPException(status_code=400, detail="配置名称已存在")
        
        config_dict = config.model_dump()
        result = dispatch_config_collection.insert_one(config_dict)
        return {"id": str(result.inserted_id), "message": "派单配置创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_description="获取派单配置列表")
async def get_dispatch_configs(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    total = dispatch_config_collection.count_documents({})
    configs = list(dispatch_config_collection.find({}).skip(skip).limit(page_size))
    
    for config in configs:
        config["_id"] = str(config["_id"])
    
    return {"data": configs, "total": total, "page": page, "page_size": page_size}

@router.get("/config/{id}", response_description="获取派单配置详情")
async def get_dispatch_config(id: str):
    config = dispatch_config_collection.find_one({"_id": ObjectId(id)})
    if config:
        config["_id"] = str(config["_id"])
        return config
    raise HTTPException(status_code=404, detail="派单配置不存在")

@router.put("/config/{id}", response_description="更新派单配置")
async def update_dispatch_config(id: str, config_update: DispatchConfigUpdate):
    config = dispatch_config_collection.find_one({"_id": ObjectId(id)})
    if not config:
        raise HTTPException(status_code=404, detail="派单配置不存在")
    
    update_data = config_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="未提供任何更新数据")
    
    result = dispatch_config_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="数据未发生变化")
    return {"message": "派单配置更新成功"}

@router.put("/config/{id}/activate", response_description="激活派单配置")
async def activate_dispatch_config(id: str):
    config = dispatch_config_collection.find_one({"_id": ObjectId(id)})
    if not config:
        raise HTTPException(status_code=404, detail="派单配置不存在")
    
    dispatch_config_collection.update_many({}, {"$set": {"is_active": False}})
    dispatch_config_collection.update_one({"_id": ObjectId(id)}, {"$set": {"is_active": True}})
    
    return {"message": "派单配置已激活"}

@router.delete("/config/{id}", response_description="删除派单配置")
async def delete_dispatch_config(id: str):
    config = dispatch_config_collection.find_one({"_id": ObjectId(id)})
    if not config:
        raise HTTPException(status_code=404, detail="派单配置不存在")
    
    if config.get("is_active"):
        raise HTTPException(status_code=400, detail="无法删除当前激活的配置，请先激活其他配置")
    
    result = dispatch_config_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="派单配置不存在")
    return {"message": "派单配置删除成功"}

@router.post("/auto/{task_id}", response_description="执行自动派单")
async def run_auto_dispatch(task_id: str, equipment_code: str):
    try:
        result = execute_dispatch(task_id, equipment_code)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "派单失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual/{task_id}", response_description="执行人工派单")
async def run_manual_dispatch(
    task_id: str, 
    equipment_code: str,
    staff_id: str,
    operator_id: str,
    operator_name: str,
    reason: str
):
    try:
        result = manual_dispatch(task_id, equipment_code, staff_id, operator_id, operator_name, reason)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "派单失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/redispatch/{task_id}", response_description="重新派单")
async def run_re_dispatch(task_id: str):
    try:
        result = re_dispatch(task_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "重新派单失败"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unlock/{task_id}", response_description="解锁人工派单锁定")
async def run_unlock_dispatch(task_id: str):
    try:
        success = unlock_manual_dispatch(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="解锁失败，任务未被人工派单锁定")
        return {"message": "已解锁人工派单锁定，任务可重新参与自动派单"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_description="获取派单统计")
async def get_statistics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    equipment_type: Optional[str] = None,
    department: Optional[str] = None
):
    try:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        result = get_dispatch_statistics(start_dt, end_dt, equipment_type, department)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_description="获取派单历史")
async def get_history(
    task_id: Optional[str] = None,
    staff_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    try:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        result = get_dispatch_history(task_id, staff_id, start_dt, end_dt, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))