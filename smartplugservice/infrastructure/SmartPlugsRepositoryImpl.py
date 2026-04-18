import json
import os
from pathlib import Path
from threading import Lock
from typing import Dict, List
import logging

from smartplugservice.application.SmartPlugsRepository import SmartPlugsRepository
from smartplugservice.domain.SmartPlug import SmartPlug
from smartplugservice.domain.SmartPlugStatus import SmartPlugStatus

logger = logging.getLogger(__name__)

class SmartPlugsRepositoryImpl(SmartPlugsRepository):
    def __init__(self, data_dir: str = ""):
        self._data_dir = Path(data_dir)

        # load data
        self._plugs_file = self._data_dir / "plugs.json"

        if not self._plugs_file.exists():
            raise FileNotFoundError(f"Plugs file not found: {self._plugs_file}")

        self._lock = Lock()

    def _read_json(self, path: Path):
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _write_json_atomic(self, path: Path, data):
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as tf:
            json.dump(data, tf, indent=2)
            tf.flush()
            os.fsync(tf.fileno())
        os.replace(tmp_path, path)

    def _load_smart_plugs(self) -> Dict[str, SmartPlug]:
        try:
            plugs_data = self._read_json(self._plugs_file)

            plugs: Dict[str, SmartPlug] = {}

            status_key = "status"
            utility_type_key = "utility_type"
            for plug_dict in plugs_data:
                if isinstance(plug_dict.get(status_key), str):
                    plug_dict[status_key] = plug_dict[status_key].lower()
                if isinstance(plug_dict.get(utility_type_key), str):
                    plug_dict[utility_type_key] = plug_dict[utility_type_key]

                plug = SmartPlug(**plug_dict)
                plugs[plug.id] = plug
            logger.debug("Loaded %d plugs from %s", len(plugs), self._plugs_file)
            return plugs
        except Exception as e:
            logger.error("Error loading plugs: %s", e)
            return {}
    def _save_plugs(self, plugs: Dict[str, SmartPlug]):
        try:
            plugs_data = []
            for plug in plugs.values():
                plugs_data.append(
                    {
                        'id': plug.id,
                        'name': plug.name,
                        'utility_type': plug.utility_type.name,
                        'status': plug.status.name,
                        'real_time_consumption': plug.real_time_consumption
                    }
                )
            self._write_json_atomic(self._plugs_file, plugs_data)
            logger.debug("Saved %d plugs to %s", len(plugs_data), self._plugs_file)
        except Exception as e:
            logger.error("Error saving plugs: %s", e)

    def get_all_plugs(self) -> List[SmartPlug]:
        with self._lock:
            plugs = self._load_smart_plugs()
            return list(plugs.values())

    def get_plug_by_id(self, plug_id: str) -> SmartPlug:
        with self._lock:
            plugs = self._load_smart_plugs()
            return plugs.get(plug_id)

    def switch_plug(self, plug_id: str) -> tuple[bool, str]:
        with self._lock:
            plugs = self._load_smart_plugs()
            plug = plugs.get(plug_id)

            if not plug:
                return False, f"Plug '{plug_id}' not found"

            if plug.status == SmartPlugStatus.ON:
                plug.status = SmartPlugStatus.OFF
            else:
                plug.status = SmartPlugStatus.ON

            plugs[plug_id] = plug
            self._save_plugs(plugs)

            return True, f"Plug '{plug_id}' status switched successfully"