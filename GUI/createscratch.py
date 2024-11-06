# createscratch.py
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import filing
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from VoronoiFortune.voronoi import VoronoiDiagram
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

        # Setting up matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_title("Click to add points")

        # Bind mouse click to add point
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def on_canvas_click(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.points.append((event.xdata, event.ydata))
            self.update_plot()

    def update_plot(self):
        # Update plot with points
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_title("Click to add points")
        points = np.array(self.points)
        if points.size > 0:
            self.ax.plot(points[:, 0], points[:, 1], 'bo')
        self.canvas.draw()

    def send_points_to_fortune(self):
        # Create Voronoi diagram
        self.points = [(float(x), float(y)) for x, y in self.points]
        print("List of tuples yang dikirim:")
        print(self.points)
        voronoi = VoronoiDiagram(self.points)
        D = voronoi.compute_diagram()

        # Clear the axes and set limits
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_title("Voronoi Diagram")

        # Plot the original points
        points = np.array(self.points)
        if points.size > 0:
            self.ax.plot(points[:, 0], points[:, 1], 'bo')

        # Extract edges from DCEL D
        edges = set()
        for half_edge in D.halfedges:
            origin = half_edge.origin
            dest = half_edge.next.origin
            x1, y1 = origin.x, origin.y
            x2, y2 = dest.x, dest.y
            # Create a sorted tuple to avoid duplicate edges
            edge = tuple(sorted([(x1, y1), (x2, y2)]))
            edges.add(edge)

        # Plot the edges
        for edge in edges:
            (x1, y1), (x2, y2) = edge
            self.ax.plot([x1, x2], [y1, y2], 'k-')

        self.canvas.draw()

    def back_to_main_menu(self):
        # Destroy the current window and call the back callback to reopen the main menu
        self.root.destroy()
        self.back_callback()
       
    def load_points_from_file(self, file_path):
        # Use the function from filing.py to load points
        self.points = filing.load_points_from_file(file_path)
        self.update_plot()

if __name__ == "__main__":
    root = tk.Tk()
    app = CreateFromScratchApp(root, lambda: None)
    root.mainloop()
