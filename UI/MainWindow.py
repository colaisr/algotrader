import time
from tkinter import *

from Main import mainMethod


class Test():
    def __init__(self,root):
        self.root = root
        self.label = Label(self.root, text="Text")

        self.button = Button(self.root,
                                text="Click to change text below",
                                command=self.changeText)
        self.button.pack()
        self.label.pack()


    def changeText(self):
        mainMethod()

    def start(self):
        self.root.mainloop()

class MainWindow:
    def __init__(self):
        self.root=Tk()

        account_frame=Frame(self.root)
        account_frame.pack(side=TOP)
        lblAccountTitle=Label(account_frame,text="Account:")
        lblAccountTitle.pack(side=LEFT)
        self.lblAccountValue=Label(account_frame,text="DU00000000:")
        self.lblAccountValue.pack(side=LEFT)




    def setLabel(self,te):
        self.lblAccountValue.configure(text="Text Updated")


    def Show(self):
        self.root.mainloop()


if __name__ == '__main__':
    # w=MainWindow()
    # w.Show()
    # w.setLabel("rrrrrrrr")
    root=Tk()
    app=Test(root)
    app.start()

