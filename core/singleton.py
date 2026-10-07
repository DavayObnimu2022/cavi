"""
Singleton-функция для фиксации текущего пользователя.
По заданию ЛР-3: создатель зафиксирован константой.
"""

class CurrentUser:
    _instance = None
    _user_id = 1
    _username = "test_user"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username


current_user = CurrentUser()


def get_current_user() -> CurrentUser:
    return current_user