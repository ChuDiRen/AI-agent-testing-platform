from typing import Any


class g_context:
    _dic: dict[str, Any] = {}

    def set_dict(self, key: str, value: Any) -> None:
        self._dic[key] = value

    def get_dict(self, key: str) -> Any | None:
        return self._dic.get(key, None)

    def set_by_dict(self, dic: dict[str, Any]) -> None:
        self._dic.update(dic)

    def show_dict(self) -> dict[str, Any]:
        return self._dic
