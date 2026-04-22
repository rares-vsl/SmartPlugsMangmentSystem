import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from smartplugservice.application.SmartPlugServiceImpl import SmartPlugsServiceImpl
from smartplugservice.domain.SmartPlug import SmartPlug
from smartplugservice.domain.SmartPlugStatus import SmartPlugStatus
from smartplugservice.domain.UtilityType import UtilityType
from smartplugservice.infrastructure.SmartPlugsRepositoryImpl import SmartPlugsRepositoryImpl

class CreateSmartPlugRequest(BaseModel):
    name: str
    utility_type: UtilityType
    status: SmartPlugStatus = SmartPlugStatus.OFF
    real_time_consumption: float = 0.0


class UpdateSmartPlugRequest(BaseModel):
    name: Optional[str] = None
    utility_type: Optional[UtilityType] = None
    status: Optional[SmartPlugStatus] = None
    real_time_consumption: Optional[float] = None


class SmartPlugsRestAPI:
    def __init__(self):
        self.repo = SmartPlugsRepositoryImpl("localdb")
        self.service = SmartPlugsServiceImpl(self.repo)
        self.app = FastAPI(
            title="SmartPlugsRest API",
            description="REST API for SmartPlugsRest household simulation environment",
            version="1.0.0"
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):

        @self.app.get("/", summary="Root endpoint")
        async def root():
            return {
                "message": "Smart Plugs API",
                "version": "1.0.0",
                "endpoints": {
                    "plugs": "/api/smart-plugs",
                    "specific_plug": "/api/smart-plugs/{plug_id}"
                }
            }

        @self.app.get("/api/smart-plugs", response_model=List[SmartPlug], summary="Get all Smart Plugs")
        async def get_all_smart_plugs():
            return self.service.get_all_plugs()

        @self.app.get("/api/smart-plugs/{plug_id}", response_model=SmartPlug, summary="Get specific Smart Plug")
        async def get_smart_plug(plug_id: str):
            plug = self.service.get_plug_by_id(plug_id)
            if not plug:
                raise HTTPException(status_code=404, detail=f"Smart plug '{plug_id}' not found")
            return plug

        @self.app.post("/api/smart-plugs", response_model=SmartPlug, status_code=201, summary="Add a new Smart Plug")
        async def create_smart_plug(body: CreateSmartPlugRequest):
            plug = SmartPlug(
                id=re.sub(r'[^a-z0-9]+', '-', body.name.lower()).strip('-'),
                name=body.name,
                utility_type=body.utility_type,
                status=body.status,
                real_time_consumption=body.real_time_consumption,
            )

            success, message = self.service.add_plug(plug)
            if not success:
                raise HTTPException(status_code=409, detail=message)
            return plug

        @self.app.put("/api/smart-plugs/{plug_id}", response_model=SmartPlug, summary="Update a Smart Plug")
        async def update_smart_plug(plug_id: str, body: UpdateSmartPlugRequest):
            existing = self.service.get_plug_by_id(plug_id)
            if not existing:
                raise HTTPException(status_code=404, detail=f"Smart plug '{plug_id}' not found")

            # Merge: only override fields that were explicitly provided
            updated = SmartPlug(
                id=plug_id,
                name=body.name if body.name is not None else existing.name,
                utility_type=body.utility_type if body.utility_type is not None else existing.utility_type,
                status=body.status if body.status is not None else existing.status,
                real_time_consumption=body.real_time_consumption if body.real_time_consumption is not None else existing.real_time_consumption,
            )
            success, message = self.service.update_plug(plug_id, updated)
            if not success:
                raise HTTPException(status_code=500, detail=message)
            return updated

        @self.app.patch("/api/smart-plugs/{plug_id}", summary="Switch Smart Plug status")
        async def switch_smart_plug_status(plug_id: str):
            plug = self.service.get_plug_by_id(plug_id)
            if not plug:
                raise HTTPException(status_code=404, detail=f"Smart plug '{plug_id}' not found")

            success, message = self.service.switch_plug(plug_id)
            if not success:
                raise HTTPException(status_code=500, detail=message)
            return {"message": message}

        @self.app.delete("/api/smart-plugs/{plug_id}", status_code=204, summary="Delete a Smart Plug")
        async def delete_smart_plug(plug_id: str):
            plug = self.service.get_plug_by_id(plug_id)
            if not plug:
                raise HTTPException(status_code=404, detail=f"Smart plug '{plug_id}' not found")

            success, message = self.service.delete_plug(plug_id)
            if not success:
                raise HTTPException(status_code=500, detail=message)