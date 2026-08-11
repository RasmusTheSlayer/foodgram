import uuid


def generate_short_code():
    return uuid.uuid4().hex[:8]
