from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import equipment, inspection, repair, maintenance, dispatch, staff

app = FastAPI(title="医疗设备巡检管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment.router, prefix="/api/equipment", tags=["设备档案"])
app.include_router(inspection.router, prefix="/api/inspection", tags=["巡检计划"])
app.include_router(repair.router, prefix="/api/repair", tags=["故障报修"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["设备维保"])
app.include_router(dispatch.router, prefix="/api/dispatch", tags=["智能派单"])
app.include_router(staff.router, prefix="/api/staff", tags=["巡检人员"])

@app.get("/")
async def root():
    return {"message": "医疗设备巡检管理系统 API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
