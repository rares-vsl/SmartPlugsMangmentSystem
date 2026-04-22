from abc import ABC, abstractmethod
from typing import List

from smartplugservice.domain.SmartPlug import SmartPlug

class SmartPlugsRepository(ABC):
    @abstractmethod
    def find_all_plugs(self) -> List[SmartPlug]:
        pass
    @abstractmethod
    def find_plug_by_id(self, plug_id: str) -> SmartPlug:
        pass
    @abstractmethod
    def switch_plug(self, plug_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    def save_plug(self, plug: SmartPlug) -> tuple[bool, str]:
        pass
    @abstractmethod
    def update_plug(self, plug_id: str, plug: SmartPlug) -> tuple[bool, str]:
        pass
    @abstractmethod
    def remove_plug(self, plug_id: str) -> tuple[bool, str]:
        pass
