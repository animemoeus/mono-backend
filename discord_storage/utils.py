import uuid


def validate_uuid(uuid_str) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return str(uuid_obj) == uuid_str
    except ValueError:
        return False
