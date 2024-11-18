import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Adjust the import path as necessary to locate your voronoi.py
from VoronoiFortune_Reiou_Error3.voronoi import Voronoi  # Import your own Voronoi class

class CreateFromScratchApp:
    def __init__(self, root, back_callback):
        self.root = root
        self.back_callback = back_callback
        self.root.title("Create from Scratch")
        self.root.geometry("800x600")

        self.points = []

        # Setting up GUI elements
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.enter_button = tk.Button(self.button_frame, text="Enter Points", command=self.send_points_to_fortune)
        self.enter_button.pack(side=tk.RIGHT)

        self.back_button = tk.Button(self.button_frame, text="Back", command=self.back_to_main_menu)
        self.back_button.pack(side=tk.LEFT)

        # Setting up tk.Canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Set data coordinate limits
        self.x_min = 0
        self.x_max = 10
        self.y_min = 0
        self.y_max = 10

        # Bind mouse click to add point
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def data_to_canvas(self, x, y):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx = (x - self.x_min) / (self.x_max - self.x_min) * width
        cy = height - ((y - self.y_min) / (self.y_max - self.y_min) * height)
        return cx, cy

    def canvas_to_data(self, cx, cy):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        x = cx / width * (self.x_max - self.x_min) + self.x_min
        y = (height - cy) / height * (self.y_max - self.y_min) + self.y_min
        return x, y

    def on_canvas_click(self, event):
        xdata, ydata = self.canvas_to_data(event.x, event.y)
        self.points.append((xdata, ydata))
        self.update_plot()

    def update_plot(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Draw the points
        for x, y in self.points:
            cx, cy = self.data_to_canvas(x, y)
            r = 3  # radius of the point
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='blue')

    def send_points_to_fortune(self):
        # Convert all numpy float64 to standard Python floats
        formatted_points = [(float(x), float(y)) for x, y in self.points]
        print("Points to be processed:", formatted_points)

        # Create Voronoi diagram using your own Voronoi class
        voronoi = Voronoi(formatted_points)
        edges = voronoi.run()

        # Plot the Voronoi diagram
        self.plot_voronoi_diagram(edges)

    def plot_voronoi_diagram(self, edges):
        # Clear the canvas
        self.canvas.delete("all")

        # Draw the points
        for x, y in self.points:
            cx, cy = self.data_to_canvas(x, y)
            r = 3  # radius of the point
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='blue')

        # Draw the edges
        edgess=[]
        for edge in edges:
            if edge.start and edge.end:
                x0, y0 = edge.start.x, edge.start.y
                x1, y1 = edge.end.x, edge.end.y
                edgess.append([x0,y0,x1,y1])
            elif edge.start and edge.direction:
                # Edge to infinity, plot as a ray in the direction
                x0, y0 = edge.start.x, 1000000000000
                x1, y1 = edge.end.x, 1000000000000
                edgess.append([cx0, cy0, cx1, cy1])
        self.drawLinesOnCanvas(edgess)
    def drawLinesOnCanvas(self, lines):
        for l in lines:
            self.canvas.create_line(l[0], l[1], l[2], l[3], fill='blue')

    def back_to_main_menu(self):
        # Destroy the current window and call the back callback to reopen the main menu
        self.root.destroy()
        self.back_callback()

    def load_points_from_file(self, file_path):
        # Load points from a file if needed
        pass  # Implement as needed

if __name__ == "__main__":
    root = tk.Tk()
    app = CreateFromScratchApp(root, lambda: None)
    root.mainloop()
