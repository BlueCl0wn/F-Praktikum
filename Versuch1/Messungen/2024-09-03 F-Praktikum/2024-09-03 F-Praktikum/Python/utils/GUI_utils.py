'''

GUI related funktions using TK

by Christian Heyn

'''


import tkinter as tk

# returns True if string s is float
def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# returns True if string s is int
def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



# TK entry field with label1 before and label2 after
# init: (inputType = 'float'/'int'/'text', text = [label1,entry,label2], size = [size_label1,size_entry,size_label2])
# create ():
class inputEntry:
    def __init__(self, parentFrame, inputType, text, size):
        self.frame =  tk.Frame(parentFrame)
        self.entryType = inputType
        self.entryText = text
        self.entrySize = size
        self.val_str   = tk.StringVar()
        def val_str_trace(*args):
            self.refresh()
        self.val_str.trace('w',val_str_trace)

    def create(self):
        #self.frame.pack(side='left')
        text1 = self.entryText[0]
        text2 = self.entryText[1]
        text3 = self.entryText[2]
        size1 = self.entrySize[0]
        size2 = self.entrySize[1]
        size3 = self.entrySize[2]
        # label 1
        label1 = tk.Label(master=self.frame, width=size1, text = text1, anchor='w')
        if len(text1)>0: label1.pack(side='left', padx=(5,0))
        # entry
        entry = tk.Entry(master=self.frame, width=size2, textvariable=self.val_str)
        entry.pack(side='left', padx = (5,0))
        self.val_str.set(text2)

        # label 2
        label2 = tk.Label(master=self.frame, width=size3, text=text3, anchor='w')
        if len(text3)>0: label2.pack(side='left', padx=(5,0))
        # Button
        def btn_callback():
            if self.test_str(self.val_str.get()):
                self.entryText[1] = self.val_str.get()
            else:
                self.val_str.set(self.entryText[1])

        return self.frame, self.val_str

    def doTest(self, s):
        if (len(s) == 0) or (s == '-'): OK = True
        else:
            if self.entryType == 'float':   OK = isFloat(s)
            if self.entryType == 'int':     OK = isInt(s)
            if self.entryType == 'text':    OK = True
        return OK

    def refresh(self):
        if self.doTest(self.val_str.get()):
            self.entryText[1] = self.val_str.get()
        else:
            self.val_str.set(self.entryText[1])



'''
# Test

window = tk.Tk()
window.geometry('500x200')
frameTest = tk.Frame(window)
frameTest.pack(side='top', anchor='w', padx=(10,0), pady=(10,0))

inputTest1 = inputEntry(frameTest, 'float', ['Voltage', '220', 'V'], [8,6,2])
frame1, value1 = inputTest1.create()
frame1.pack(side='top', anchor='w', pady=(0,10))

inputTest2 = inputEntry(frameTest, 'float', ['Current', '1.8', 'A'], [8,6,2])
frame2, value2 = inputTest2.create()
frame2.pack(side='top', anchor='w', pady=(0,10))

inputTest3 = inputEntry(frameTest, 'int',   ['Frequency', '30000', 'Hz'], [8,6,2])
frame3, value3 = inputTest3.create()
frame3.pack(side='top', anchor='w', pady=(0,10))

inputTest4 = inputEntry(frameTest, 'int',   ['Integer [m]', '18', ''], [8,6,0])
frame4, value4 = inputTest4.create()
frame4.pack(side='top', anchor='w', pady=(0,10))


window.mainloop()
'''
