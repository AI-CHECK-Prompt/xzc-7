from fastapi import APIRouter, HTTPException
from app.database import staff_collection
from app.models.dispatch import Staff, StaffUpdate
from bson import ObjectId
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.post("/", response_description="创建巡检人员")
async def create_staff(staff: Staff):
    try:
        existing = staff_collection.find_one({"staff_id": staff.staff_id})
        if existing:
            raise HTTPException(status_code=400, detail="人员ID已存在")
        
        staff_dict = staff.model_dump()
        result = staff_collection.insert_one(staff_dict)
        return {"id": str(result.inserted_id), "message": "巡检人员创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_description="获取巡检人员列表")
async def get_staff_list(
    page: int = 1, 
    page_size: int = 10, 
    department: Optional[str] = None, 
    shift_status: Optional[str] = None,
    status: Optional[str] = None
):
    query = {}
    if department:
        query["department"] = department
    if shift_status:
        query["shift_status"] = shift_status
    if status:
        query["status"] = status
    
    skip = (page - 1) * page_size
    total = staff_collection.count_documents(query)
    staff_list = list(staff_collection.find(query).skip(skip).limit(page_size))
    
    for staff in staff_list:
        staff["_id"] = str(staff["_id"])
        if isinstance(staff.get("work_start_time"), datetime):
            staff["work_start_time"] = staff["work_start_time"].isoformat()
    
    return {"data": staff_list, "total": total, "page": page, "page_size": page_size}

@router.get("/{id}", response_description="获取巡检人员详情")
async def get_staff(id: str):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if staff:
        staff["_id"] = str(staff["_id"])
        if isinstance(staff.get("work_start_time"), datetime):
            staff["work_start_time"] = staff["work_start_time"].isoformat()
        return staff
    raise HTTPException(status_code=404, detail="巡检人员不存在")

@router.get("/by-staff-id/{staff_id}", response_description="根据人员ID获取详情")
async def get_staff_by_staff_id(staff_id: str):
    staff = staff_collection.find_one({"staff_id": staff_id})
    if staff:
        staff["_id"] = str(staff["_id"])
        if isinstance(staff.get("work_start_time"), datetime):
            staff["work_start_time"] = staff["work_start_time"].isoformat()
        return staff
    raise HTTPException(status_code=404, detail="巡检人员不存在")

@router.put("/{id}", response_description="更新巡检人员")
async def update_staff(id: str, staff_update: StaffUpdate):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    update_data = staff_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    result = staff_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在或未更新")
    return {"message": "巡检人员更新成功"}

@router.put("/{id}/location", response_description="更新人员实时位置")
async def update_staff_location(id: str, latitude: float, longitude: float):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    result = staff_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"real_time_location": {"latitude": latitude, "longitude": longitude}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在或未更新")
    return {"message": "人员位置更新成功"}

@router.put("/{id}/shift-status", response_description="更新人员值班状态")
async def update_staff_shift_status(id: str, shift_status: str):
    valid_status = ["在岗", "休息", "请假", "离线", "交接班"]
    if shift_status not in valid_status:
        raise HTTPException(status_code=400, detail=f"值班状态必须是: {', '.join(valid_status)}")
    
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    result = staff_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"shift_status": shift_status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在或未更新")
    return {"message": "值班状态更新成功"}

@router.put("/{id}/start-work", response_description="开始工作")
async def start_work(id: str):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    result = staff_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"work_start_time": datetime.now(), "shift_status": "在岗"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在或未更新")
    return {"message": "已开始工作"}

@router.put("/{id}/end-work", response_description="结束工作")
async def end_work(id: str):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    result = staff_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"work_start_time": None, "shift_status": "休息"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在或未更新")
    return {"message": "已结束工作"}

@router.delete("/{id}", response_description="删除巡检人员")
async def delete_staff(id: str):
    staff = staff_collection.find_one({"_id": ObjectId(id)})
    if not staff:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    
    if staff.get("current_task_count", 0) > 0:
        raise HTTPException(status_code=400, detail="该人员当前有任务在执行，无法删除")
    
    result = staff_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="巡检人员不存在")
    return {"message": "巡检人员删除成功"}