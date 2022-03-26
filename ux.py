
from tkinter import *
class page():
    def __init__(self):
        # Set self.data = current working directory files
        self.data = []
    
    def gui(self):
        pass

def gui(size, logo=None, title=None):

    # Initialize tkinter widget
    root = Tk()

    # Create main start up page
    label = Label(root, text='Testing')
    label.pack()

    root.mainloop()

gui()

