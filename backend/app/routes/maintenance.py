from fastapi import APIRouter, HTTPException
from app.database import maintenance_collection, equipment_collection
from app.models.maintenance import MaintenanceCycle, MaintenancePlan, MaintenanceTask, MaintenanceRecord, MaintenanceReminder
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/cycle", response_description="创建维保周期配置")
async def create_maintenance_cycle(cycle: MaintenanceCycle):
    try:
        cycle_dict = cycle.model_dump()
        cycle_dict["created_at"] = datetime.now()
        result = maintenance_collection.insert_one(cycle_dict)
        return {"id": str(result.inserted_id), "message": "维保周期配置创建成功"}
    except Exception as e:
        if "duplicate key" in str(e):
            raise HTTPException(status_code=400, detail="设备编号已存在周期配置")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cycle", response_description="获取维保周期配置列表")
async def get_maintenance_cycles(page: int = 1, page_size: int = 10, equipment_code: Optional[str] = None, status: Optional[str] = None):
    query = {"type": "cycle"}
    if equipment_code:
        query["equipment_code"] = equipment_code
    if status:
        query["status"] = status
    
    skip = (page - 1) * page_size
    total = maintenance_collection.count_documents(query)
    cycles = list(maintenance_collection.find(query).skip(skip).limit(page_size))
    
    for cycle in cycles:
        cycle["_id"] = str(cycle["_id"])
    
    return {"data": cycles, "total": total, "page": page, "page_size": page_size}

@router.get("/cycle/{id}", response_description="获取维保周期配置详情")
async def get_maintenance_cycle(id: str):
    cycle = maintenance_collection.find_one({"_id": ObjectId(id), "type": "cycle"})
    if cycle:
        cycle["_id"] = str(cycle["_id"])
        return cycle
    raise HTTPException(status_code=404, detail="维保周期配置不存在")

@router.put("/cycle/{id}", response_description="更新维保周期配置")
async def update_maintenance_cycle(id: str, cycle_update: dict):
    result = maintenance_collection.update_one({"_id": ObjectId(id), "type": "cycle"}, {"$set": cycle_update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="维保周期配置不存在或未更新")
    return {"message": "维保周期配置更新成功"}

@router.delete("/cycle/{id}", response_description="删除维保周期配置")
async def delete_maintenance_cycle(id: str):
    result = maintenance_collection.delete_one({"_id": ObjectId(id), "type": "cycle"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="维保周期配置不存在")
    return {"message": "维保周期配置删除成功"}

@router.post("/plan", response_description="创建维保计划")
async def create_maintenance_plan(plan: MaintenancePlan):
    try:
        plan_dict = plan.model_dump()
        plan_dict["type"] = "plan"
        plan_dict["created_at"] = datetime.now()
        result = maintenance_collection.insert_one(plan_dict)
        
        equipment_list = list(equipment_collection.find({"equipment_code": {"$in": plan.equipment_codes}}))
        task_list = []
        for eq in equipment_list:
            task = {
                "type": "task",
                "plan_id": str(result.inserted_id),
                "equipment_code": eq["equipment_code"],
                "equipment_name": eq.get("name", ""),
                "scheduled_date": plan.start_date,
                "assignee": plan.assignee,
                "status": "待执行",
                "created_at": datetime.now()
            }
            task_list.append(task)
        
        if task_list:
            maintenance_collection.insert_many(task_list)
        
        return {"id": str(result.inserted_id), "message": "维保计划创建成功，已自动生成维保任务"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plan", response_description="获取维保计划列表")
async def get_maintenance_plans(page: int = 1, page_size: int = 10, status: Optional[str] = None, assignee: Optional[str] = None):
    query = {"type": "plan"}
    if status:
        query["status"] = status
    if assignee:
        query["assignee"] = assignee
    
    skip = (page - 1) * page_size
    total = maintenance_collection.count_documents(query)
    plans = list(maintenance_collection.find(query).skip(skip).limit(page_size))
    
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    
    return {"data": plans, "total": total, "page": page, "page_size": page_size}

@router.get("/plan/{id}", response_description="获取维保计划详情")
async def get_maintenance_plan(id: str):
    plan = maintenance_collection.find_one({"_id": ObjectId(id), "type": "plan"})
    if plan:
        plan["_id"] = str(plan["_id"])
        tasks = list(maintenance_collection.find({"plan_id": id, "type": "task"}))
        for task in tasks:
            task["_id"] = str(task["_id"])
        plan["tasks"] = tasks
        return plan
    raise HTTPException(status_code=404, detail="维保计划不存在")

@router.put("/plan/{id}", response_description="更新维保计划")
async def update_maintenance_plan(id: str, plan_update: dict):
    result = maintenance_collection.update_one({"_id": ObjectId(id), "type": "plan"}, {"$set": plan_update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="维保计划不存在或未更新")
    return {"message": "维保计划更新成功"}

@router.delete("/plan/{id}", response_description="删除维保计划")
async def delete_maintenance_plan(id: str):
    maintenance_collection.delete_many({"plan_id": id, "type": "task"})
    result = maintenance_collection.delete_one({"_id": ObjectId(id), "type": "plan"})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="维保计划不存在")
    return {"message": "维保计划删除成功"}

@router.get("/task", response_description="获取维保任务列表")
async def get_maintenance_tasks(page: int = 1, page_size: int = 10, status: Optional[str] = None, assignee: Optional[str] = None, equipment_code: Optional[str] = None):
    query = {"type": "task"}
    if status:
        query["status"] = status
    if assignee:
        query["assignee"] = assignee
    if equipment_code:
        query["equipment_code"] = equipment_code
    
    skip = (page - 1) * page_size
    total = maintenance_collection.count_documents(query)
    tasks = list(maintenance_collection.find(query).skip(skip).limit(page_size))
    
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return {"data": tasks, "total": total, "page": page, "page_size": page_size}

@router.put("/task/{id}", response_description="更新维保任务")
async def update_maintenance_task(id: str, task_update: dict):
    if "actual_date" in task_update:
        task_update["actual_date"] = datetime.now()
    result = maintenance_collection.update_one({"_id": ObjectId(id), "type": "task"}, {"$set": task_update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="维保任务不存在或未更新")
    
    task = maintenance_collection.find_one({"_id": ObjectId(id), "type": "task"})
    if task and task.get("status") == "已完成":
        equipment_collection.update_one(
            {"equipment_code": task["equipment_code"]},
            {"$set": {"status": "正常"}}
        )
    
    return {"message": "维保任务更新成功"}

@router.post("/record", response_description="提交维保记录")
async def submit_maintenance_record(record: MaintenanceRecord):
    try:
        record_dict = record.model_dump()
        record_dict["type"] = "record"
        record_dict["created_at"] = datetime.now()
        result = maintenance_collection.insert_one(record_dict)
        
        equipment_collection.update_one(
            {"equipment_code": record.equipment_code},
            {"$push": {"maintenance_records": record_dict}}
        )
        
        return {"id": str(result.inserted_id), "message": "维保记录提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/record", response_description="获取维保记录列表")
async def get_maintenance_records(page: int = 1, page_size: int = 10, equipment_code: Optional[str] = None, overall_status: Optional[str] = None):
    query = {"type": "record"}
    if equipment_code:
        query["equipment_code"] = equipment_code
    if overall_status:
        query["overall_status"] = overall_status
    
    skip = (page - 1) * page_size
    total = maintenance_collection.count_documents(query)
    records = list(maintenance_collection.find(query).sort("maintenance_date", -1).skip(skip).limit(page_size))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return {"data": records, "total": total, "page": page, "page_size": page_size}

@router.get("/record/{equipment_code}", response_description="获取设备维保记录")
async def get_equipment_maintenance_records(equipment_code: str):
    query = {"type": "record", "equipment_code": equipment_code}
    records = list(maintenance_collection.find(query).sort("maintenance_date", -1))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records

@router.get("/reminder", response_description="获取维保提醒列表")
async def get_maintenance_reminders(page: int = 1, page_size: int = 10, reminder_status: Optional[str] = None):
    query = {"type": "reminder"}
    if reminder_status:
        query["reminder_status"] = reminder_status
    
    skip = (page - 1) * page_size
    total = maintenance_collection.count_documents(query)
    reminders = list(maintenance_collection.find(query).skip(skip).limit(page_size))
    
    for reminder in reminders:
        reminder["_id"] = str(reminder["_id"])
    
    return {"data": reminders, "total": total, "page": page, "page_size": page_size}

@router.post("/reminder/generate", response_description="生成维保提醒")
async def generate_maintenance_reminders():
    try:
        today = datetime.now()
        
        cycles = list(maintenance_collection.find({"type": "cycle", "status": "启用"}))
        
        reminder_count = 0
        for cycle in cycles:
            equipment = equipment_collection.find_one({"equipment_code": cycle["equipment_code"]})
            if not equipment:
                continue
            
            last_maintenance = equipment.get("maintenance_records", [])
            if last_maintenance:
                last_date = max([r.get("maintenance_date", datetime.min) for r in last_maintenance])
            else:
                last_date = equipment.get("purchase_date", datetime.min)
            
            next_due_date = last_date + timedelta(days=cycle["interval_days"])
            days_remaining = (next_due_date - today).days
            
            if 0 <= days_remaining <= cycle["reminder_days"]:
                existing_reminder = maintenance_collection.find_one({
                    "type": "reminder",
                    "equipment_code": cycle["equipment_code"],
                    "reminder_status": "未处理"
                })
                
                if not existing_reminder:
                    reminder = {
                        "type": "reminder",
                        "equipment_code": cycle["equipment_code"],
                        "equipment_name": equipment.get("name", ""),
                        "due_date": next_due_date,
                        "days_remaining": days_remaining,
                        "assignee": cycle.get("assignee", ""),
                        "reminder_status": "未处理",
                        "created_at": datetime.now()
                    }
                    maintenance_collection.insert_one(reminder)
                    reminder_count += 1
        
        overdue_tasks = maintenance_collection.find({
            "type": "task",
            "status": "待执行",
            "scheduled_date": {"$lt": today}
        })
        for task in overdue_tasks:
            maintenance_collection.update_one(
                {"_id": task["_id"]},
                {"$set": {"status": "逾期"}}
            )
        
        return {"message": f"维保提醒生成成功，共生成 {reminder_count} 条提醒"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reminder/{id}", response_description="处理维保提醒")
async def handle_maintenance_reminder(id: str, reminder_update: dict):
    result = maintenance_collection.update_one({"_id": ObjectId(id), "type": "reminder"}, {"$set": reminder_update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="维保提醒不存在或未更新")
    return {"message": "维保提醒处理成功"}