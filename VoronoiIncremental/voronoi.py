from DCEL import *

def create_bounding_box(dcel, points, margin=10):
    x_min = min(point[0] for point in points) - margin
    y_min = min(point[1] for point in points) - margin
    x_max = max(point[0] for point in points) + margin
    y_max = max(point[1] for point in points) + margin

    # Create vertices for the bounding box corners
    v1 = Vertex(x_min, y_min)  # Bottom-left
    v2 = Vertex(x_max, y_min)  # Bottom-right
    v3 = Vertex(x_max, y_max)  # Top-right
    v4 = Vertex(x_min, y_max)  # Top-left

    # Create half-edges that connect the vertices
    e1 = HalfEdge(origin=v1)
    e2 = HalfEdge(origin=v2)
    e3 = HalfEdge(origin=v3)
    e4 = HalfEdge(origin=v4)

    # Link the half-edges to form a closed loop
    e1.next = e2
    e2.next = e3
    e3.next = e4
    e4.next = e1
    e1.prev = e4
    e2.prev = e1
    e3.prev = e2
    e4.prev = e3

    bounding_face = Face(outer_component=e1)

    # Link the edges to face
    e1.incident_face = bounding_face
    e2.incident_face = bounding_face
    e3.incident_face = bounding_face
    e4.incident_face = bounding_face

    dcel.faces.append(bounding_face)
    dcel.half_edges.extend([e1, e2, e3, e4])
    dcel.vertices.extend([v1, v2, v3, v4])

    print(f"Bounding box created with vertices at ({x_min}, {y_min}), ({x_max}, {y_min}), ({x_max}, {y_max}), ({x_min}, {y_max})")

def build_voronoi(dcel, points):
    for point in points:
        region = locate_region(dcel, point)  
        split_region(dcel, region, point)  

def locate_region(dcel, point):
    current_face = dcel.faces[0]

    while True:
        inside = True 
        edge = current_face.outer_component
        start_edge = edge
        while True:
            if not is_point_left_of_edge(point, edge):
                # If the point is not inside, move to the adjacent face
                inside = False
                current_face = edge.twin.incident_face 
                break
            edge = edge.next
            if edge == start_edge:
                break 
        if inside:
            return current_face

def is_point_left_of_edge(point, edge):
    origin = edge.origin
    destination = edge.next.origin

    edge_vector = (destination.x - origin.x, destination.y - origin.y)
    point_vector = (point[0] - origin.x, point[1] - origin.y)
    cross_product = edge_vector[0] * point_vector[1] - edge_vector[1] * point_vector[0]
    return cross_product > 0  

def split_region(dcel, region, point):
    #TODO: Create new edges and faces to update the DCEL for the new point
    pass


