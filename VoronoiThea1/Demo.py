import tkinter as tk
from Voronoi import Voronoi

class MainWindow:
    # Initial radius of drawn points on canvas
    INITIAL_RADIUS = 3

    # flag to lock the canvas when drawn
    LOCK_FLAG = False

    def __init__(self, master, points=None, reopen_main_menu=None):
        self.master = master
        self.master.title("Voronoi")

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=700, height=600)
        self.w.config(background='white')
        self.w.bind('<Double-1>', self.onDoubleClick)
        self.w.pack(fill=tk.BOTH, expand=1)

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()

        self.btnCalculate = tk.Button(self.frmButton, text='Calculate', width=20, command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)

        self.btnClear = tk.Button(self.frmButton, text='Clear', width=20, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)

        self.btnVerbose = tk.Button(self.frmButton, text='Exit Verbose', width=20, command=self.onClickVerbose)
        self.btnVerbose.pack(side=tk.LEFT)

        self.btnExit = tk.Button(self.frmButton, text='Exit', width=20, command=self.onClickClose)
        self.btnExit.pack(side=tk.LEFT)

        self.verbose = True
        self.label = True
        self.haveLines = False

        self.points = points  # store the points

        # Initialize zoom and pan variables
        self.scale = 1.0  # Current scale
        self.translate_x = 0  # Current translation x
        self.translate_y = 0  # Current translation y

        # Bind mouse events for zooming and panning
        self.w.bind('<MouseWheel>', self.zoom)  # For Windows and Linux
        self.w.bind('<Button-4>', self.zoom)    # For macOS scroll up
        self.w.bind('<Button-5>', self.zoom)    # For macOS scroll down
        self.w.bind('<ButtonPress-1>', self.pan_start)
        self.w.bind('<B1-Motion>', self.pan_move)

        # If points are provided, display them on the canvas
        if self.points:
            self.display_points(self.points)

        self.reopen_main_menu = reopen_main_menu

    def display_points(self, points):
        for x, y in points:
            self.draw_point(x, y)

    def draw_point(self, x, y):
        # Adjust the radius inversely proportional to the scale
        adjusted_radius = self.INITIAL_RADIUS / self.scale
        self.w.create_oval(
            x - adjusted_radius, y - adjusted_radius,
            x + adjusted_radius, y + adjusted_radius,
            fill="black", tag=("point", "no_scale")
        )
        t = "   " + str(int(x)) + " " + str(int(y))
        if self.label:
            self.w.create_text(
                x, y, anchor="s",
                font=("Ariel", int(7 / self.scale)),
                text=t, tag=("label", "no_scale")
            )

    def onClickCalculate(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            pObj = self.w.find_withtag("point")
            points = []
            for p in pObj:
                coord = self.w.coords(p)
                x = (coord[0] + coord[2]) / 2  # Calculate the center x-coordinate
                y = (coord[1] + coord[3]) / 2  # Calculate the center y-coordinate
                points.append((x, y))

            vp = Voronoi(points)
            vp.verbose = self.verbose
            vp.process()
            lines = vp.get_output()
            self.drawLinesOnCanvas(lines)
            self.haveLines = True

            # Get the largest empty circles
            largest_circles = vp.get_largest_empty_circles()
            self.drawCirclesOnCanvas(largest_circles)

    def drawCirclesOnCanvas(self, circles):
        for circle in circles:
            center, radius = circle
            x0 = center.x - radius
            y0 = center.y - radius
            x1 = center.x + radius
            y1 = center.y + radius
            self.w.create_oval(x0, y0, x1, y1, outline='red', width=2, tag="circle")

    def onClickClose(self):
        self.master.destroy()
        if self.reopen_main_menu:
            self.reopen_main_menu()

    def onClickVerbose(self):
        if self.verbose is False:
            self.btnVerbose['text'] = 'Exit Verbose'
            self.verbose = True
        else:
            self.btnVerbose['text'] = 'Set Verbose'
            self.verbose = False

    def onClickClear(self):
        self.LOCK_FLAG = False
        if self.haveLines:
            self.w.delete('line')
            self.w.delete('circle')
            self.haveLines = False
        else:
            self.w.delete(tk.ALL)
            self.points = None

    def onDoubleClick(self, event):
        if not self.LOCK_FLAG:
            x = self.w.canvasx(event.x)
            y = self.w.canvasy(event.y)
            self.draw_point(x, y)

    def drawLinesOnCanvas(self, lines):
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill='blue', tag="line")

    def zoom(self, event):
        # Respond to mouse wheel event
        if event.num == 4 or event.delta > 0:
            # Zoom in
            scale_factor = 1.1
        elif event.num == 5 or event.delta < 0:
            # Zoom out
            scale_factor = 0.9
        else:
            # Unknown event, do nothing
            return

        # Get mouse position
        x = self.w.canvasx(event.x)
        y = self.w.canvasy(event.y)

        # Scale the canvas
        self.scale *= scale_factor

        # Scale all items except those tagged with 'no_scale'
        for item in self.w.find_all():
            if "no_scale" not in self.w.gettags(item):
                self.w.scale(item, x, y, scale_factor, scale_factor)

        # Adjust point sizes and label fonts
        self.update_point_sizes()
        self.update_label_sizes()

        # Update scroll region
        self.w.configure(scrollregion=self.w.bbox("all"))

    def update_point_sizes(self):
        # Adjust the size of the points based on the current scale
        for point in self.w.find_withtag("point"):
            x0, y0, x1, y1 = self.w.coords(point)
            x = (x0 + x1) / 2
            y = (y0 + y1) / 2
            adjusted_radius = self.INITIAL_RADIUS / self.scale
            self.w.coords(
                point,
                x - adjusted_radius, y - adjusted_radius,
                x + adjusted_radius, y + adjusted_radius
            )

    def update_label_sizes(self):
        # Adjust the font size of labels based on the current scale
        new_font_size = max(int(7 / self.scale), 1)
        for label in self.w.find_withtag("label"):
            self.w.itemconfig(label, font=("Ariel", new_font_size))

    def pan_start(self, event):
        self.w.scan_mark(event.x, event.y)

    def pan_move(self, event):
        self.w.scan_dragto(event.x, event.y, gain=1)

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()