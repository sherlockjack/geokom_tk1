def load_points_from_file(file_path):
    """
    Load points from a file. Each line in the file should contain two numbers separated by a space, comma, or tab.
    Example of file content:
    1.0, 2.5
    3.0, 4.5
    """
    points = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    x_str, y_str = line.strip().replace(',', ' ').split()
                    x = float(x_str)
                    y = float(y_str)
                    points.append((x, y))
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    return points
