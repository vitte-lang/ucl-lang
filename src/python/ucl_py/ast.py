from dataclasses import dataclass
from typing import List, Any

@dataclass
class Program:
    items: List[Any]

@dataclass
class Assignment:
    key: str
    value: Any

@dataclass
class Section:
    name: str
    body: List[Any]
