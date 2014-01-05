import Tkinter
from PIL import Image, ImageTk

class PreviewWindow():

    def __init__(self, img, size):
        self.root = Tkinter.Tk()
        self.root.geometry('%dx%d' % (size[0]+20,size[1]))
        self.root.bind('<Key>', self.OnKeyPress)
        self.root.focus_force()
        self.scrollbar = Tkinter.Scrollbar(self.root)
        self.scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.tkpi = ImageTk.PhotoImage(img)
        self.canvas_image = Tkinter.Canvas(self.root, width=1000, height=650)
        self.canvas_image.create_image(0,0, anchor=Tkinter.NW, image=self.tkpi)
        self.canvas_image.pack()
        self.canvas_image.config(yscrollcommand=self.scrollbar.set,
                            scrollregion=self.canvas_image.bbox(Tkinter.ALL))
        self.scrollbar.config(command=self.canvas_image.yview)
        self.root.title('poster preview')
        self.root.mainloop()

    def OnKeyPress(self, event):
        if event.keysym == 'space' or event.char == 'q' or event.char == 'Q':
            self.root.destroy()
        elif event.keysym == 'Down' or event.char == 'j' or event.char == 'J':
            self.canvas_image.yview_scroll(1, 'units')
        elif event.keysym == 'Up' or event.char == 'k' or event.char == 'K':
            self.canvas_image.yview_scroll(-1, 'units')

