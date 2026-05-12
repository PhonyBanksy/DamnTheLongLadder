import tkinter as tk

# Initial coordinates
x, y, w, h = 2930,1245,160,110

class DraggableOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.6)

        self.root.update_idletasks()

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        print(f'Detectedto say what to fuck screen: {self.screen_w}x{self.screen_h}')

        actual_x = x
        actual_y = y

        self.root.geometry(f'{w}x{h}+{actual_x}+{actual_y}')
        self.root.configure(bg='red')

        self.canvas = tk.Canvas(self.root, width=w, height=h,
                                bg='red', highlightthickness=2,
                                highlightbackground='blue')
        self.canvas.pack()

        self.label = tk.Label(self.root, text=f'{x},{y}',
                              bg='red', fg='white', font=('Arial', 6))
        self.label.place(x=0, y=0)

        self._drag_x = 0
        self._drag_y = 0

        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.label.bind('<ButtonPress-1>', self.on_press)
        self.label.bind('<B1-Motion>', self.on_drag)

        # Right-click to close
        self.canvas.bind('<ButtonPress-3>', lambda e: self.root.destroy())

        self.root.mainloop()

    def on_press(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def on_drag(self, event):
        cur_x = self.root.winfo_x()
        cur_y = self.root.winfo_y()
        new_x = cur_x + event.x - self._drag_x
        new_y = cur_y + event.y - self._drag_y

        self.root.geometry(f'+{new_x}+{new_y}')
        self.label.config(text=f'{new_x},{new_y}')
        print(f'"x": {new_x}, "y": {new_y}, "w": {w}, "h": {h}')

DraggableOverlay()