import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CreateFromScratchApp:
    def __init__(self, root):
        self.root = root
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
        # Placeholder function to handle points
        # This function will send points to the Fortune algorithm (to be implemented)
        print("Points to be processed:", self.points)

if __name__ == "__main__":
    root = tk.Tk()
    app = CreateFromScratchApp(root)
    root.mainloop()
