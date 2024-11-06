import heapq

class PointHeap:
    def __init__(self, points):
        self.points = [(y,x) for x,y in points]
        heapq.heapify(self.points)

    def pop(self):
        popped = heapq.heappop(self.points)
        return (popped[1], popped[0])

    def push(self, point):
        heapq.heappush(self.points, (point[1], point[0]))