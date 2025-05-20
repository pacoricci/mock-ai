from typing import Any, Dict


class BaseSettings:
    model_config: Dict[str, Any] = {}

    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def model_fields(self):
        return self.__dict__.keys()

    def model_dump(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def model_copy(self):
        return self.__class__(**self.model_dump())


SettingsConfigDict = dict
