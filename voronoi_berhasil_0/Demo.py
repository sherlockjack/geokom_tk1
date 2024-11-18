# original Python version by
# Janson Hendryli 
# Tarumanagara University
# Jakarta, Indonesia
# jansonhendryli@gmail.com
# https://github.com/jansonh/Voronoi

import tkinter as tk

from Voronoi import Voronoi

class MainWindow:
    # radius of drawn points on canvas
    RADIUS = 1

    
    # flag to lock the canvas when drawn
    LOCK_FLAG = False
    
    def __init__(self, master):
        self.master = master
        self.master.title("Voronoi")

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=700, height=600)
        self.w.config(background='white')
        self.w.bind('<Double-1>', self.onDoubleClick)
        self.w.pack()       

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()
        
        self.btnCalculate = tk.Button(self.frmButton, text='Calculate', \
                                      width=20, command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)
        
        self.btnClear = tk.Button(self.frmButton, text='Clear', \
                                  width=20, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)

        self.btnVerbose = tk.Button(self.frmButton, text='Exit Verbose', \
                                    width=20, command=self.onClickVerbose)
        self.btnVerbose.pack(side=tk.LEFT)

        self.btnExit = tk.Button(self.frmButton, text='Exit',width=20, \
                                 command=self.onClickClose)
        self.btnExit.pack(side=tk.LEFT)

        self.verbose = True
        self.label = True
        self.haveLines = False
        
    def onClickCalculate(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            pObj = self.w.find_withtag("point")
            points = []
            for p in pObj:
                coord = self.w.coords(p)
                points.append((coord[0] + self.RADIUS, coord[1] + self.RADIUS))

            vp = Voronoi(points)
            vp.verbose = self.verbose
            vp.process()
            lines = vp.get_output()
            self.drawLinesOnCanvas(lines)
            self.haveLines = True

            # Get the largest empty circles
            largest_circles = vp.get_largest_empty_circles()
            self.drawCirclesOnCanvas(largest_circles)
                
            #for L in lines:
            #   print(L)


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
        
    def onClickVerbose(self):
        if self.verbose is False:
            self.btnVerbose['text'] = 'Exit Verbose'
            self.verbose = True
        else:
            self.btnVerbose['text'] = 'Set Verbose'
            self.verbose = False
        
    def onClickClear(self):
        self.LOCK_FLAG = False
        #self.w.delete(tk.ALL)
        if self.haveLines:
            self.w.delete('line')
            self.haveLines = False
        else:
            self.w.delete(tk.ALL)

    def onDoubleClick(self, event):
        if not self.LOCK_FLAG:
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, \
                event.x+self.RADIUS, event.y+self.RADIUS, fill="black", tag="point")
            t =   "   "+str(event.x)+" "+str(event.y)
            if self.label: self.w.create_text(event.x,event.y,anchor="s", \
                font=("Ariel", 7),text=t, tag="label")

    def drawLinesOnCanvas(self, lines):
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill='blue', tag="line")

def main(): 
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
