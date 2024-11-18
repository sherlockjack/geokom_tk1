from voronoi import *

if __name__ == '__main__':
    dcel = DCEL()
    points = [(10, 20), (30, 40), (50, 60), (70, 80)]
    
    create_bounding_box(dcel, points)
    
    print("Vertices of the bounding box:")
    for vertex in dcel.vertices:
        print(f"Vertex at ({vertex.x}, {vertex.y})")

    print("\nHalf-edges of the bounding box:")
    for edge in dcel.half_edges:
        if edge.origin:
            print(f"Half-edge starting at ({edge.origin.x}, {edge.origin.y})")