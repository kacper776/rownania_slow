from base import *
from graph import *
from queue import Queue


def bfs(start: Node, max_len: int) -> dict:
    if start.terminal():
        return start.variable_subs
    q = Queue()
    q.put(start)
    visited = {hash(start)}
    while not q.empty():
        node = q.get()
        for child in node.children():
            child_hash = hash(child)
            if child_hash not in visited and len(child) <= max_len:
                visited.add(child_hash)
                if child.terminal():
                    return child.variable_subs
                q.put(child)
    return {}
