from pymongo import MongoClient
from pymongo.collection import Collection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    logger.info("MongoDB连接成功")
except Exception as e:
    logger.warning(f"MongoDB连接失败: {e}")
    client = MongoClient("mongodb://localhost:27017/")

db = client["medical_equipment"]

equipment_collection: Collection = db["equipment"]
inspection_collection: Collection = db["inspection"]
repair_collection: Collection = db["repair"]

try:
    equipment_collection.create_index("equipment_code", unique=True)
    logger.info("索引创建成功")
except Exception as e:
    logger.warning(f"索引创建失败: {e}")
