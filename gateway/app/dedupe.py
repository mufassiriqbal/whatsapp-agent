from collections import OrderedDict
from threading import Lock


_seen: OrderedDict[str, None] = OrderedDict()
_lock = Lock()
_MAX_ENTRIES = 10_000


def mark_seen(message_id: str) -> bool:
    with _lock:
        if message_id in _seen:
            return False

        _seen[message_id] = None
        if len(_seen) > _MAX_ENTRIES:
            _seen.popitem(last=False)
        return True
