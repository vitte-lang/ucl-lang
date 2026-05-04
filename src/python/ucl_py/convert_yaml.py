def to_yaml(d):
    return '\n'.join(f"{k}: {v}" for k,v in d.items())
