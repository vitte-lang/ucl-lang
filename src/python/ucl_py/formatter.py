def format_program(program):
    lines = []
    for s in program.items:
        if hasattr(s, 'key'):
            lines.append(f"{s.key} = {repr(s.value)};")
        elif hasattr(s, 'name'):
            lines.append(f"{s.name} {{")
            for inner in s.body:
                lines.append(f"  {inner.key} = {repr(inner.value)};")
            lines.append("}")
    return "\n".join(lines)
