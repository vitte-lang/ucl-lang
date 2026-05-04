# =========================================================
# UCL AST — MAX ∞
# typed / positional / visitors / transform / serialize
# =========================================================

from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict, Optional, Union


# ===================== Position =====================

@dataclass
class Position:
    line: int
    column: int
    file: Optional[str] = None


# ===================== Base Node =====================

@dataclass
class Node:
    pos: Optional[Position] = None

    def accept(self, visitor):
        method = getattr(visitor, f"visit_{self.__class__.__name__}", None)
        if method:
            return method(self)
        return visitor.generic_visit(self)


# ===================== Literals =====================

@dataclass
class Literal(Node):
    value: Any = None


@dataclass
class String(Literal):
    value: str = ""


@dataclass
class Number(Literal):
    value: Union[int, float] = 0


@dataclass
class Boolean(Literal):
    value: bool = False


@dataclass
class Null(Literal):
    value: None = None


# ===================== Expressions =====================

@dataclass
class Variable(Node):
    name: str = ""


@dataclass
class BinaryOp(Node):
    op: str = ""
    left: Node = None
    right: Node = None


@dataclass
class UnaryOp(Node):
    op: str = ""
    operand: Node = None


@dataclass
class FunctionCall(Node):
    name: str = ""
    args: List[Node] = field(default_factory=list)


# ===================== Collections =====================

@dataclass
class ListNode(Node):
    elements: List[Node] = field(default_factory=list)


@dataclass
class MapEntry(Node):
    key: str = ""
    value: Node = None


@dataclass
class MapNode(Node):
    entries: List[MapEntry] = field(default_factory=list)


# ===================== Statements =====================

@dataclass
class Assignment(Node):
    key: List[str] = field(default_factory=list)
    value: Node = None


@dataclass
class Section(Node):
    name: str = ""
    body: List[Node] = field(default_factory=list)


@dataclass
class Include(Node):
    path: str = ""


@dataclass
class Conditional(Node):
    condition: Node = None
    then_branch: List[Node] = field(default_factory=list)
    else_branch: List[Node] = field(default_factory=list)


# ===================== Advanced =====================

@dataclass
class Profile(Node):
    name: str = ""
    body: List[Node] = field(default_factory=list)


@dataclass
class Module(Node):
    name: str = ""
    body: List[Node] = field(default_factory=list)


@dataclass
class Macro(Node):
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[Node] = field(default_factory=list)


@dataclass
class SchemaField(Node):
    key: List[str] = field(default_factory=list)
    type_name: str = ""
    constraints: List[str] = field(default_factory=list)


@dataclass
class Schema(Node):
    name: str = ""
    fields: List[SchemaField] = field(default_factory=list)


# ===================== Program =====================

@dataclass
class Program(Node):
    body: List[Node] = field(default_factory=list)


# ===================== Visitor =====================

class Visitor:
    def generic_visit(self, node):
        for attr in vars(node).values():
            if isinstance(attr, Node):
                attr.accept(self)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, Node):
                        item.accept(self)


# ===================== Transformer =====================

class Transformer(Visitor):
    def generic_visit(self, node):
        for k, v in vars(node).items():
            if isinstance(v, Node):
                setattr(node, k, v.accept(self))
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    if isinstance(item, Node):
                        new_list.append(item.accept(self))
                    else:
                        new_list.append(item)
                setattr(node, k, new_list)
        return node


# ===================== Serializer =====================

def to_dict(node: Node) -> Dict[str, Any]:
    if node is None:
        return None

    data = {
        "type": node.__class__.__name__,
        "pos": asdict(node.pos) if node.pos else None
    }

    for k, v in vars(node).items():
        if k == "pos":
            continue

        if isinstance(v, Node):
            data[k] = to_dict(v)
        elif isinstance(v, list):
            data[k] = [to_dict(x) if isinstance(x, Node) else x for x in v]
        else:
            data[k] = v

    return data


# ===================== Validation =====================

class Validator(Visitor):
    def __init__(self):
        self.errors = []

    def error(self, msg, node):
        self.errors.append({
            "msg": msg,
            "pos": node.pos
        })

    def visit_Assignment(self, node: Assignment):
        if not node.key:
            self.error("empty key", node)
        if node.value is None:
            self.error("missing value", node)
        self.generic_visit(node)

    def visit_FunctionCall(self, node: FunctionCall):
        if not node.name:
            self.error("missing function name", node)
        self.generic_visit(node)


# ===================== Pretty Printer =====================

class PrettyPrinter(Visitor):
    def __init__(self):
        self.indent = 0

    def pad(self):
        return "  " * self.indent

    def visit_Program(self, node):
        for stmt in node.body:
            stmt.accept(self)

    def visit_Assignment(self, node):
        print(self.pad() + ".".join(node.key) + " = ...")

    def visit_Section(self, node):
        print(self.pad() + node.name + " {")
        self.indent += 1
        for stmt in node.body:
            stmt.accept(self)
        self.indent -= 1
        print(self.pad() + "}")
