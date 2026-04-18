from typing import List

from fastapi import FastAPI, HTTPException

from starlette.middleware.cors import CORSMiddleware

from smartplugservice.application.SmartPlugServiceImpl import SmartPlugsServiceImpl
from smartplugservice.domain.SmartPlug import SmartPlug
from smartplugservice.infrastructure.SmartPlugsRepositoryImpl import SmartPlugsRepositoryImpl


class SmartPlugsRestAPI:
    def __init__(self):
        """
        Initialize the WavesLab API application.
        """
        self.repo  = SmartPlugsRepositoryImpl("localdb")
        self.service = SmartPlugsServiceImpl(self.repo)
        self.app = FastAPI(
            title="SmartPlugsRest API",
            description="REST API for SmartPlugsRest household simulation environment",
            version="1.0.0"
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "*"
            ],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):
        """Set up all API routes."""

        @self.app.get("/", summary="Root endpoint")
        async def root():
            """Root endpoint with basic information."""
            return {
                "message": "Smart Plugs API",
                "version": "1.0.0",
                "endpoints": {
                    "nodes": "/api/smart-plugs",
                    "specific_node": "/api/smart-plugs/{slug}"
                }
            }

        @self.app.get("/api/smart-plugs", response_model=List[SmartPlug], summary="Get all Smart Plugs")
        async def get_all_smart_plugs():
            """
            Retrieve all SmartPlugs in the system.

            Returns a list of all SmartPlugs with their current status and configuration.
            """
            plugs = self.service.get_all_plugs()
            return plugs

        @self.app.get("/api/smart-plugs/{plug_id}", response_model=SmartPlug, summary="Get specific Smart Plug")
        async def get_smart_plug(plug_id: str):
            """
             Retrieve details of a specific Smart Plug by its plugID.

            Args:
                plug_id: The unique ID of the Smart Plug

            Returns:
                Smart Plug details
            """
            plug = self.service.get_plug_by_id(plug_id)

            if not plug:
                raise HTTPException(status_code=404, detail=f"Smart plug with ID '{plug_id}' not found")

            return plug

        @self.app.patch("/api/smart-plugs/{plug_id}", summary="Switch Smart Plug status")
        async def update_smart_plug_status(plug_id: str):
            """
             Switch Smart Plug status by its plugID.

            Args:
                plug_id: The unique ID of the Smart Plug

            Returns:
                The result of the switch
            """
            plug = self.service.get_plug_by_id(plug_id)

            if not plug:
                raise HTTPException(status_code=404, detail=f"Smart plug with ID '{plug_id}' not found")

            updated_plug, result_msg = self.service.switch_plug(plug_id)

            if not updated_plug:
                raise HTTPException(status_code=500, detail="Failed to update node")

            return result_msg

