def evaluate(program):
    out = {}
    def walk(items, prefix=""):
        for s in items:
            if hasattr(s, 'key'):
                out[prefix + s.key] = s.value
            elif hasattr(s, 'name'):
                walk(s.body, prefix + s.name + ".")
    walk(program.items)
    return out
