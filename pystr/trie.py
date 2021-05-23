from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrieNode:
    label: Optional[int] = None
    out: dict[str, TrieNode] = field(default_factory=dict, init=False)


@dataclass
class Trie:
    root: TrieNode = field(default_factory=TrieNode, init=False)

    def insert(self, x: str, label: int):
        n = self.root
        for i in range(len(x)):
            if x[i] not in n.out:
                n.out[x[i]] = TrieNode()
            n = n.out[x[i]]
        n.label = label

    def __contains__(self, x: str) -> bool:
        n = self.root
        for i in range(len(x)):
            if x[i] not in n.out:
                return False
            n = n.out[x[i]]
        return n.label is not None
