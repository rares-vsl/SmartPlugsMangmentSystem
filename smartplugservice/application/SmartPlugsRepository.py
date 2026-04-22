from abc import ABC, abstractmethod
from typing import List

from smartplugservice.domain.SmartPlug import SmartPlug

class SmartPlugsRepository(ABC):
    @abstractmethod
    def get_all_plugs(self) -> List[SmartPlug]:
        pass
    @abstractmethod
    def get_plug_by_id(self, plug_id: str) -> SmartPlug:
        pass
    @abstractmethod
    def switch_plug(self, plug_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    def add_plug(self, plug: SmartPlug) -> tuple[bool, str]:
        pass
    @abstractmethod
    def update_plug(self, plug_id: str, plug: SmartPlug) -> tuple[bool, str]:
        pass
    @abstractmethod
    def delete_plug(self, plug_id: str) -> tuple[bool, str]:
        pass
