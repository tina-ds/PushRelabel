"""Highest-label Push-Relabel implementation from the research notebook."""

import math

from .base import Edge, PushRelabel


class PushRelabelHighest(PushRelabel):
    """Run the notebook's highest-label Push-Relabel control flow.

    The bucket selection, LIFO order, and post-relabel requeue behavior are
    preserved. Only the final flow calculation is corrected to use sink excess.
    """

    def __init__(self, number_of_vertices: int):
        super().__init__(
            number_of_vertices,
            use_global=False,
            use_gap=False,
        )

    def _push(
        self,
        u: int,
        e: Edge,
        excess,
        height,
        is_active,
        buckets,
        current_max_h,
        source: int,
        sink: int,
    ):

        v = e.to
        delta = min(excess[u], e.cap)
        if delta <= 0:
            return current_max_h

        e.cap -= delta
        self.g[v][e.rev].cap += delta

        excess[u] -= delta
        excess[v] += delta

        if v != source and v != sink and (not is_active[v]) and excess[v] > 0:
            h_v = height[v]
            buckets[h_v].append(v)
            is_active[v] = True
            if h_v > current_max_h:
                current_max_h = h_v

        return current_max_h

    def _relabel(self, u: int, height):

        n = self.n
        min_h = math.inf
        for e in self.g[u]:
            if e.cap > 0 and height[e.to] < min_h:
                min_h = height[e.to]
        if min_h < math.inf:
            height[u] = min_h + 1
        else:
            height[u] = 2 * n

    def max_flow(self, source: int, sink: int) -> int:

        n = self.n
        g = self.g

        height = [0] * n
        excess = [0] * n
        height[source] = n

        max_height = 2 * n
        buckets = [[] for _ in range(max_height + 1)]
        is_active = [False] * n

        current_max_h = 0
        for e in g[source]:
            if e.cap > 0:
                delta = e.cap
                e.cap -= delta
                g[e.to][e.rev].cap += delta
                excess[e.to] += delta
                excess[source] -= delta
                if e.to != source and e.to != sink and excess[e.to] > 0:
                    h_v = height[e.to]
                    buckets[h_v].append(e.to)
                    is_active[e.to] = True
                    if h_v > current_max_h:
                        current_max_h = h_v

        while True:
            while (
                current_max_h >= 0
                and current_max_h <= max_height
                and not buckets[current_max_h]
            ):
                current_max_h -= 1

            if current_max_h < 0:
                break

            u = buckets[current_max_h].pop()
            is_active[u] = False

            if excess[u] <= 0 or u == source or u == sink:
                continue

            while excess[u] > 0:
                pushed = False
                for e in g[u]:
                    v = e.to
                    if e.cap > 0 and height[u] == height[v] + 1:
                        current_max_h = self._push(
                            u,
                            e,
                            excess,
                            height,
                            is_active,
                            buckets,
                            current_max_h,
                            source,
                            sink,
                        )
                        pushed = True
                        if excess[u] == 0:
                            break

                if not pushed:
                    old_h = height[u]
                    self._relabel(u, height)
                    new_h = height[u]
                    if new_h > max_height:
                        new_h = max_height
                        height[u] = max_height

                    if excess[u] > 0:
                        buckets[new_h].append(u)
                        is_active[u] = True
                        if new_h > current_max_h:
                            current_max_h = new_h
                    break

        return excess[sink]
