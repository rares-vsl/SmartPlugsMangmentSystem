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
