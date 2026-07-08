from fastapi import APIRouter, HTTPException
from app.database import equipment_collection
from app.models.equipment import Equipment, EquipmentUpdate
from bson import ObjectId
from typing import List, Optional

router = APIRouter()

@router.post("/", response_description="创建设备")
async def create_equipment(equipment: Equipment):
    try:
        result = equipment_collection.insert_one(equipment.model_dump())
        return {"id": str(result.inserted_id), "message": "设备创建成功"}
    except Exception as e:
        if "duplicate key" in str(e):
            raise HTTPException(status_code=400, detail="设备编号已存在")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_description="获取所有设备")
async def get_equipment_list(page: int = 1, page_size: int = 10, department: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if department:
        query["department"] = department
    if status:
        query["status"] = status
    
    skip = (page - 1) * page_size
    total = equipment_collection.count_documents(query)
    equipment_list = list(equipment_collection.find(query).skip(skip).limit(page_size))
    
    for item in equipment_list:
        item["_id"] = str(item["_id"])
    
    return {"data": equipment_list, "total": total, "page": page, "page_size": page_size}

@router.get("/{id}", response_description="获取设备详情")
async def get_equipment(id: str):
    equipment = equipment_collection.find_one({"_id": ObjectId(id)})
    if equipment:
        equipment["_id"] = str(equipment["_id"])
        return equipment
    raise HTTPException(status_code=404, detail="设备不存在")

@router.put("/{id}", response_description="更新设备")
async def update_equipment(id: str, equipment_update: EquipmentUpdate):
    update_data = equipment_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    result = equipment_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="设备不存在或未更新")
    return {"message": "设备更新成功"}

@router.delete("/{id}", response_description="删除设备")
async def delete_equipment(id: str):
    result = equipment_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="设备不存在")
    return {"message": "设备删除成功"}

@router.get("/search/{keyword}", response_description="搜索设备")
async def search_equipment(keyword: str):
    query = {
        "$or": [
            {"equipment_code": {"$regex": keyword, "$options": "i"}},
            {"name": {"$regex": keyword, "$options": "i"}},
            {"model": {"$regex": keyword, "$options": "i"}},
            {"department": {"$regex": keyword, "$options": "i"}}
        ]
    }
    equipment_list = list(equipment_collection.find(query))
    for item in equipment_list:
        item["_id"] = str(item["_id"])
    return equipment_list

@router.get("/department/list", response_description="获取科室列表")
async def get_department_list():
    departments = equipment_collection.distinct("department")
    return departments
