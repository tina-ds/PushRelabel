"""Baseline Push-Relabel implementation extracted from the research notebook."""

from collections import deque
import math
from collections.abc import Sequence


class Edge:
    __slots__ = ("to", "rev", "cap")

    def __init__(self, to: int, rev: int, cap: int):
        self.to = to
        self.rev = rev
        self.cap = cap


class PushRelabel:
    def __init__(
        self,
        n: int,
        use_global: bool = False,
        use_gap: bool = False,
        global_freq: int | None = None,
    ):

        self.n = n
        self.g = [[] for _ in range(n)]

        self.use_global = use_global
        self.use_gap = use_gap

        if global_freq is None:
            self.global_freq = max(1, n)
        else:
            self.global_freq = max(1, global_freq)

        self._relabel_counter = 0

    def add_edge(self, u: int, v: int, cap: int):

        fwd = Edge(v, len(self.g[v]), cap)
        rev = Edge(u, len(self.g[u]), 0)
        self.g[u].append(fwd)
        self.g[v].append(rev)

    def _push(
        self,
        u: int,
        e: Edge,
        excess,
        height,
        active,
        in_queue,
        s: int,
        t: int,
    ):

        v = e.to
        delta = min(excess[u], e.cap)
        if delta <= 0:
            return

        e.cap -= delta
        self.g[v][e.rev].cap += delta

        excess[u] -= delta
        excess[v] += delta

        if v != s and v != t and (not in_queue[v]) and excess[v] > 0:
            active.append(v)
            in_queue[v] = True

    def _relabel(
        self,
        u: int,
        height,
        count,
        excess,
        active,
        in_queue,
        s: int,
        t: int,
    ):

        n = self.n
        old_h = height[u]

        min_h = math.inf
        for e in self.g[u]:
            if e.cap > 0 and height[e.to] < min_h:
                min_h = height[e.to]

        if min_h < math.inf:
            new_h = min_h + 1
        else:
            new_h = 2 * n

        count[old_h] -= 1
        if new_h < len(count):
            count[new_h] += 1
        height[u] = new_h

        if self.use_gap and 0 <= old_h < n and count[old_h] == 0:
            self._gap(old_h, height, count, excess, active, in_queue, s, t)

    def _gap(
        self,
        k: int,
        height,
        count,
        excess,
        active,
        in_queue,
        s: int,
        t: int,
    ):

        n = self.n
        for v in range(n):
            h_v = height[v]
            if k < h_v < n:
                count[h_v] -= 1
                height[v] = n
                count[n] += 1

        active.clear()
        for v in range(n):
            in_queue[v] = False
        for v in range(n):
            if v != s and v != t and excess[v] > 0 and height[v] < 2 * n:
                active.append(v)
                in_queue[v] = True

    def _global_relabel(
        self,
        s: int,
        t: int,
        height,
        excess,
        active,
        in_queue,
        count,
    ):

        n = self.n
        INF = 2 * n
        previous_height = height.copy()

        for v in range(n):
            height[v] = INF
        height[t] = 0

        q = deque([t])

        while q:
            v = q.popleft()
            hv = height[v]
            for e in self.g[v]:
                rev_edge = self.g[e.to][e.rev]
                if rev_edge.cap > 0 and height[e.to] == INF:
                    height[e.to] = hv + 1
                    q.append(e.to)

        # Preserve label progress outside the sink-reachable residual region.
        # Resetting these vertices on every global relabel can repeat the same state.
        for v in range(n):
            if v != s and height[v] == INF:
                height[v] = max(previous_height[v], n + 1)

        height[s] = n

        for i in range(len(count)):
            count[i] = 0
        for v in range(n):
            h_v = height[v]
            if h_v < len(count):
                count[h_v] += 1

        active.clear()
        for v in range(n):
            in_queue[v] = False
        for v in range(n):
            if v != s and v != t and excess[v] > 0 and height[v] < 2 * n:
                active.append(v)
                in_queue[v] = True

        self._relabel_counter = 0

    def max_flow(self, s: int, t: int) -> int:

        n = self.n
        g = self.g

        height = [0] * n
        excess = [0] * n
        height[s] = n

        count = [0] * (2 * n + 1)
        for v in range(n):
            count[height[v]] += 1

        active = deque()
        in_queue = [False] * n

        for e in g[s]:
            if e.cap > 0:
                delta = e.cap
                e.cap -= delta
                g[e.to][e.rev].cap += delta
                excess[e.to] += delta
                excess[s] -= delta
                if e.to != s and e.to != t:
                    active.append(e.to)
                    in_queue[e.to] = True

        while active:
            u = active.popleft()
            in_queue[u] = False

            while excess[u] > 0:
                pushed = False
                for e in g[u]:
                    v = e.to
                    if e.cap > 0 and height[u] == height[v] + 1:
                        self._push(u, e, excess, height, active, in_queue, s, t)
                        pushed = True
                        if excess[u] == 0:
                            break

                if not pushed:
                    self._relabel(u, height, count, excess, active, in_queue, s, t)
                    self._relabel_counter += 1

                    if self.use_global and self._relabel_counter >= self.global_freq:
                        self._global_relabel(
                            s, t, height, excess, active, in_queue, count
                        )
                        break

                    if height[u] >= 2 * n:
                        break

        return excess[t]


def compute_max_flow(
    number_of_vertices: int,
    edges: Sequence[tuple[int, int, int]],
    source: int,
    sink: int,
) -> int:
    """Compute maximum flow with the baseline Push–Relabel implementation.

    The implementation was extracted from the research notebook. The returned
    flow is taken from the sink excess to avoid counting residual entries created
    by edges entering the source.
    """

    push_relabel = PushRelabel(
        number_of_vertices,
        use_global=False,
        use_gap=False,
    )
    for from_vertex, to_vertex, capacity in edges:
        push_relabel.add_edge(from_vertex, to_vertex, capacity)

    return push_relabel.max_flow(source, sink)
