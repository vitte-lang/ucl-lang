def validate(data: dict, schema: dict):
    errors = []
    for k, typ in schema.items():
        if k not in data:
            errors.append((k, "missing"))
    return errors
