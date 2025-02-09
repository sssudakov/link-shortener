import shortuuid

def generate_short_code(length=6, original_url=None):
    return shortuuid.uuid(name=original_url)[:length] if original_url else shortuuid.ShortUUID().random(length=length)
