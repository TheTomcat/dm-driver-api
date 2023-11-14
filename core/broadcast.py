from broadcaster import Broadcast


def make_channel(session_id: int) -> str:
    return f"sess{session_id}"


broadcast = Broadcast("memory://")

# https://github.com/tiangolo/fastapi/issues/3009
# https://github.com/encode/broadcaster
