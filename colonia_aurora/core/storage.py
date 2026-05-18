import threading


class DataStorage:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._data = {}
                    inst._history = {}
                    inst._rw_lock = threading.RLock()
                    cls._instance = inst
        return cls._instance

    def get(self, key: str, default=None):
        with self._rw_lock:
            return self._data.get(key, default)

    def set(self, key: str, value):
        with self._rw_lock:
            self._data[key] = value
            if key not in self._history:
                self._history[key] = []
            self._history[key].append(value)

    def history(self, key: str, last_n: int = None) -> list:
        with self._rw_lock:
            h = self._history.get(key, [])
            if last_n is None:
                return list(h)
            return list(h[-last_n:])

    def snapshot(self) -> dict:
        with self._rw_lock:
            return dict(self._data)
