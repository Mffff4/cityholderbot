import json
import os
from typing import Dict, Optional

class SessionProxyManager:
    def __init__(self):
        self.mapping_file = "session_proxy_mapping.json"
        self.mapping: Dict[str, str] = self._load_mapping()

    def _load_mapping(self) -> Dict[str, str]:
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_mapping(self):
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=4)

    def assign_proxy(self, session_name: str, proxy: str):
        self.mapping[session_name] = proxy
        self._save_mapping()

    def get_proxy(self, session_name: str) -> Optional[str]:
        return self.mapping.get(session_name)

    def remove_session(self, session_name: str):
        if session_name in self.mapping:
            del self.mapping[session_name]
            self._save_mapping() 