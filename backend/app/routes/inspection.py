from fastapi import APIRouter, HTTPException
from app.database import inspection_collection
from app.models.inspection import InspectionPlan, InspectionTask, InspectionRecord, InspectionPlanUpdate, InspectionTaskUpdate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/plan", response_description="创建巡检计划")
async def create_inspection_plan(plan: InspectionPlan):
    try:
        plan_dict = plan.model_dump()
        plan_dict["created_at"] = datetime.now()
        result = inspection_collection.insert_one(plan_dict)
        return {"id": str(result.inserted_id), "message": "巡检计划创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan", response_description="获取巡检计划列表")
async def get_inspection_plans(page: int = 1, page_size: int = 10, status: Optional[str] = None):
    query = {"$or": [{"type": "plan"}, {"type": {"$exists": False}}]}
    if status:
        query["status"] = status
    
    skip = (page - 1) * page_size
    total = inspection_collection.count_documents(query)
    plans = list(inspection_collection.find(query).skip(skip).limit(page_size))
    
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    
    return {"data": plans, "total": total, "page": page, "page_size": page_size}

@router.get("/plan/{id}", response_description="获取巡检计划详情")
async def get_inspection_plan(id: str):
    plan = inspection_collection.find_one({"_id": ObjectId(id)})
    if plan:
        plan["_id"] = str(plan["_id"])
        return plan
    raise HTTPException(status_code=404, detail="巡检计划不存在")

@router.put("/plan/{id}", response_description="更新巡检计划")
async def update_inspection_plan(id: str, plan_update: InspectionPlanUpdate):
    plan = inspection_collection.find_one({"_id": ObjectId(id)})
    if not plan:
        raise HTTPException(status_code=404, detail="巡检计划不存在")
    
    update_data = plan_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="未提供任何更新数据")
    
    result = inspection_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="数据未发生变化")
    return {"message": "巡检计划更新成功"}

@router.delete("/plan/{id}", response_description="删除巡检计划")
async def delete_inspection_plan(id: str):
    result = inspection_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="巡检计划不存在")
    return {"message": "巡检计划删除成功"}

@router.post("/task", response_description="创建巡检任务")
async def create_inspection_task(task: InspectionTask):
    try:
        task_dict = task.model_dump()
        task_dict["type"] = "task"
        task_dict["created_at"] = datetime.now()
        result = inspection_collection.insert_one(task_dict)
        return {"id": str(result.inserted_id), "message": "巡检任务创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task", response_description="获取巡检任务列表")
async def get_inspection_tasks(page: int = 1, page_size: int = 10, status: Optional[str] = None, assignee: Optional[str] = None):
    query = {"type": "task"}
    if status:
        query["status"] = status
    if assignee:
        query["assignee"] = assignee
    
    skip = (page - 1) * page_size
    total = inspection_collection.count_documents(query)
    tasks = list(inspection_collection.find(query).skip(skip).limit(page_size))
    
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return {"data": tasks, "total": total, "page": page, "page_size": page_size}

@router.put("/task/{id}", response_description="更新巡检任务")
async def update_inspection_task(id: str, task_update: InspectionTaskUpdate):
    task = inspection_collection.find_one({"_id": ObjectId(id)})
    if not task:
        raise HTTPException(status_code=404, detail="巡检任务不存在")
    
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="未提供任何更新数据")
    
    result = inspection_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="数据未发生变化")
    return {"message": "巡检任务更新成功"}

@router.post("/record", response_description="提交巡检记录")
async def submit_inspection_record(record: InspectionRecord):
    try:
        record_dict = record.model_dump()
        record_dict["type"] = "record"
        record_dict["created_at"] = datetime.now()
        result = inspection_collection.insert_one(record_dict)
        return {"id": str(result.inserted_id), "message": "巡检记录提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/record/{equipment_code}", response_description="获取设备巡检记录")
async def get_inspection_records(equipment_code: str):
    query = {"type": "record", "equipment_code": equipment_code}
    records = list(inspection_collection.find(query).sort("inspection_date", -1))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records
