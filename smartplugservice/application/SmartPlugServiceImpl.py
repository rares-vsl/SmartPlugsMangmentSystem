from typing import List

from smartplugservice.application.SmartPlugService import SmartPlugsService
from smartplugservice.application.SmartPlugsRepository import SmartPlugsRepository
from smartplugservice.domain.SmartPlug import SmartPlug


class SmartPlugsServiceImpl(SmartPlugsService):
    def __init__(self, repository: SmartPlugsRepository):
        self.repository = repository

    def get_all_plugs(self) -> List[SmartPlug]:
        return self.repository.find_all_plugs()

    def get_plug_by_id(self, plug_id: str) -> SmartPlug:
        return self.repository.find_plug_by_id(plug_id)

    def switch_plug(self, plug_id: str) -> tuple[bool, str]:
        return self.repository.switch_plug(plug_id)

    def add_plug(self, plug: SmartPlug) -> tuple[bool, str]:
        return self.repository.save_plug(plug)

    def update_plug(self, plug_id: str, plug: SmartPlug) -> tuple[bool, str]:
        return self.repository.update_plug(plug_id, plug)

    def delete_plug(self, plug_id: str) -> tuple[bool, str]:
        return self.repository.remove_plug(plug_id)

    def get_statistics(self):
        plugs = self.repository.find_all_plugs()

        stats = {
            "plugs_by_status": {
                "ON": [],
                "OFF": []
            },
            "plugs_by_utility": {},
            "consumption": {
                "total": 0.0
            }
        }

        for plug in plugs:
            # Group by Status
            status_key = plug.status.value.upper()
            stats["plugs_by_status"][status_key].append(plug)

            utility_key = plug.utility_type.value
            if utility_key not in stats["plugs_by_utility"]:
                stats["plugs_by_utility"][utility_key] = []
            stats["plugs_by_utility"][utility_key].append(plug)

            if status_key == "ON":
                stats["consumption"]["total"] += plug.real_time_consumption
                stats["consumption"][utility_key] = (
                        stats["consumption"].get(utility_key, 0.0) + plug.real_time_consumption
                )

        return stats