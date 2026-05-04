def to_toml(d):
    return '\n'.join(f"{k} = {repr(v)}" for k,v in d.items())
