from pymongo import MongoClient
from pymongo.collection import Collection
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/medical_equipment")

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    logger.info("MongoDB连接成功")
except Exception as e:
    logger.warning(f"MongoDB连接失败: {e}")
    client = MongoClient("mongodb://localhost:27017/")

db = client["medical_equipment"]

equipment_collection: Collection = db["equipment"]
inspection_collection: Collection = db["inspection"]
repair_collection: Collection = db["repair"]
maintenance_collection: Collection = db["maintenance"]
staff_collection: Collection = db["staff"]
dispatch_config_collection: Collection = db["dispatch_config"]
dispatch_history_collection: Collection = db["dispatch_history"]
dispatch_lock_collection: Collection = db["dispatch_lock"]

try:
    equipment_collection.create_index("equipment_code", unique=True)
    maintenance_collection.create_index("type")
    maintenance_collection.create_index("equipment_code")
    
    staff_collection.create_index("staff_id", unique=True)
    staff_collection.create_index("shift_status")
    staff_collection.create_index("department")
    staff_collection.create_index("status")
    
    dispatch_config_collection.create_index("config_name")
    dispatch_config_collection.create_index("is_active")
    
    dispatch_history_collection.create_index("task_id")
    dispatch_history_collection.create_index("selected_staff_id")
    dispatch_history_collection.create_index("dispatch_time")
    dispatch_history_collection.create_index("equipment_code")
    
    dispatch_lock_collection.create_index("task_id", unique=True)
    dispatch_lock_collection.create_index("expires_at")
    dispatch_lock_collection.create_index("is_active")
    
    logger.info("索引创建成功")
except Exception as e:
    logger.warning(f"索引创建失败: {e}")
