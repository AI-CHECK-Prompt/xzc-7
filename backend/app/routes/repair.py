from fastapi import APIRouter, HTTPException
from app.database import repair_collection, equipment_collection
from app.models.repair import RepairOrder, RepairUpdate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/", response_description="创建报修单")
async def create_repair_order(order: RepairOrder):
    try:
        order_dict = order.model_dump()
        order_dict["created_at"] = datetime.now()
        order_dict["updated_at"] = datetime.now()
        result = repair_collection.insert_one(order_dict)
        
        equipment_collection.update_one(
            {"equipment_code": order.equipment_code},
            {"$set": {"status": "故障"}}
        )
        
        return {"id": str(result.inserted_id), "message": "报修单创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_description="获取报修单列表")
async def get_repair_orders(page: int = 1, page_size: int = 10, status: Optional[str] = None, priority: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    
    skip = (page - 1) * page_size
    total = repair_collection.count_documents(query)
    orders = list(repair_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size))
    
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return {"data": orders, "total": total, "page": page, "page_size": page_size}

@router.get("/{id}", response_description="获取报修单详情")
async def get_repair_order(id: str):
    order = repair_collection.find_one({"_id": ObjectId(id)})
    if order:
        order["_id"] = str(order["_id"])
        return order
    raise HTTPException(status_code=404, detail="报修单不存在")

@router.put("/{id}", response_description="更新报修单")
async def update_repair_order(id: str, order_update: RepairUpdate):
    update_data = order_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="没有提供更新数据")
    
    update_data["updated_at"] = datetime.now()
    
    old_order = repair_collection.find_one({"_id": ObjectId(id)})
    if not old_order:
        raise HTTPException(status_code=404, detail="报修单不存在")
    
    result = repair_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="报修单不存在或未更新")
    
    new_order = repair_collection.find_one({"_id": ObjectId(id)})
    if new_order and old_order.get("status") != "已完成" and new_order.get("status") == "已完成":
        equipment_code = new_order["equipment_code"]
        unfinished_count = repair_collection.count_documents({
            "equipment_code": equipment_code,
            "_id": {"$ne": ObjectId(id)},
            "status": {"$nin": ["已完成", "已取消"]}
        })
        if unfinished_count == 0:
            equipment_collection.update_one(
                {"equipment_code": equipment_code},
                {"$set": {"status": "正常"}}
            )
    
    return {"message": "报修单更新成功"}

@router.delete("/{id}", response_description="删除报修单")
async def delete_repair_order(id: str):
    result = repair_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="报修单不存在")
    return {"message": "报修单删除成功"}

@router.get("/equipment/{equipment_code}", response_description="获取设备报修记录")
async def get_equipment_repair_records(equipment_code: str):
    query = {"equipment_code": equipment_code}
    records = list(repair_collection.find(query).sort("created_at", -1))
    
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records
