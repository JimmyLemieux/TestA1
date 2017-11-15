from ctypes import *
from os import *
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *
from tkinter import simpledialog
from datetime import *

class Calendar(Structure):
    _fields_ = [
        ("version", c_float),
        ("prodID", c_byte * 1000),
        ("events", c_void_p),
        ("properties", c_void_p)]

class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.previousIndex = -1;
        self.openFile = ""
        self.setupCal()

    def printCalend(self):
		
        filename = self.openFile
        fStr = filename.encode('utf-8')
        
        calPtr = POINTER(Calendar)()

        self.logPrint(('returned = ',self.createCal(fStr,byref(calPtr)))) #notice the type

        testCal = calPtr.contents
        self.logPrint(('version = ', testCal.version))

        stuff = cast(testCal.prodID, c_char_p)

        self.logPrint(stuff.value.decode("utf-8"))
        
        calStr = self.printCal(calPtr)
        self.logPrint(calStr.decode("ISO-8859-1"))

    def setupCal(self):
        calLibPath = './bin/icallib.so'
        self.callib = CDLL(calLibPath)

        self.createCal = self.callib.createCalendar
        self.createCal.argtypes = [c_char_p,POINTER(POINTER(Calendar))]
        self.createCal.restype = c_int

        self.printCal = self.callib.printCalendar
        self.printCal.restype = c_char_p
        
        self.numEvents = self.callib.getNumOfEvents
        self.numEvents.argtypes = [POINTER(Calendar)]
        self.numEvents.restype = c_int
        
        
    def displayFileView(self):
        calPtr = POINTER(Calendar)()
        fStr = self.openFile.encode('utf-8')
        errNum = self.createCal(fStr, byref(calPtr))
        
        calStr = self.printCal(calPtr)
        #self.logPrint(calStr.decode("ISO-8859-1"))
        
        numOfEvents = self.numEvents(calPtr)
        self.logPrint("Number of Events: " + str(numOfEvents))

    def init_window(self):
        self.master.title("iCalGUI")
        self.pack(fill=BOTH, expand=1)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu)
        file.add_command(label="Open...", command=self.open, accelerator="Ctrl+O")
        file.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file.add_command(label="Save as...", command=self.saveAs, accelerator="Ctrl+Z")
        file.add_command(label="Exit", command=self.exit, accelerator="Ctrl+X")
        root.bind('<Control-o>', self.open)
        root.bind('<Control-s>', self.save)
        root.bind('<Control-z>', self.saveAs)
        root.bind('<Control-x>', self.exit)
        root.bind('<Escape>', self.exit)

        create = Menu(menu)
        create.add_command(label="Create calendar", command=self.createCal)
        create.add_command(label="Create event", command=self.createEvt)#state="disabled" at start and set to normal if a calendar is in use

        help = Menu(menu)
        help.add_command(label="About iCalGUI...", command=self.about)

        menu.add_cascade(label="File", menu=file)
        menu.add_cascade(label="Create", menu=create)
        menu.add_cascade(label="Help", menu=help)

        fileView = Frame(root)
        fileView.pack(fill="both", expand=True)
        fileView.grid_rowconfigure(0, weight=1)
        fileView.grid_rowconfigure(1, weight=1)
        fileView.grid_rowconfigure(2, weight=1)
        fileView.grid_rowconfigure(3, weight=1)
        fileView.grid_rowconfigure(4, weight=1)

        fileView.grid_columnconfigure(0, weight=1)
        fileView.grid_columnconfigure(1, weight=1)
        fileView.grid_columnconfigure(2, weight=1)
        fileView.grid_columnconfigure(3, weight=5)

        self.label = Label(fileView, text="Event No", relief="sunken")
        self.label.grid(row=0, column=0, sticky="sew")

        self.label = Label(fileView, text="Props", relief="sunken")
        self.label.grid(row=0, column=1, sticky="sew")

        self.label = Label(fileView, text="Alarms", relief="sunken")
        self.label.grid(row=0, column=2, sticky="sew")

        self.label = Label(fileView, text="Summary", relief="sunken")
        self.label.grid(row=0, column=3, sticky="sew")

        self.listbox = Listbox(fileView, exportselection=0, yscrollcommand=self.yscroll1)
        self.listbox.grid(row=1, column=0, sticky="nsew")

        self.listbox2 = Listbox(fileView, exportselection=0, yscrollcommand=self.yscroll2)
        self.listbox2.grid(row=1, column=1, sticky="nsew")

        self.listbox3 = Listbox(fileView, exportselection=0, yscrollcommand=self.yscroll3)
        self.listbox3.grid(row=1, column=2, sticky="nsew")

        self.listbox4 = Listbox(fileView, exportselection=0, yscrollcommand=self.yscroll4)
        self.listbox4.grid(row=1, column=3, sticky="nsew", columnspan=5)

        def onSelect(evt):
            w = evt.widget
            index = int(w.curselection()[0])

            if self.previousIndex == index:
                self.listbox.selection_clear(0, END)
                self.listbox2.selection_clear(0, END)
                self.listbox3.selection_clear(0, END)
                self.listbox4.selection_clear(0, END)
                self.previousIndex = -1
            else:
                self.listbox.selection_clear(0, END)
                self.listbox2.selection_clear(0, END)
                self.listbox3.selection_clear(0, END)
                self.listbox4.selection_clear(0, END)
                self.listbox.select_set(index)
                self.listbox2.select_set(index)
                self.listbox3.select_set(index)
                self.listbox4.select_set(index)
                self.previousIndex = index
            self.update_idletasks()

            value = w.get(index)

        self.listbox.bind('<<ListboxSelect>>', onSelect)
        self.listbox2.bind('<<ListboxSelect>>', onSelect)
        self.listbox3.bind('<<ListboxSelect>>', onSelect)
        self.listbox4.bind('<<ListboxSelect>>', onSelect)

        for x in range(0, 8):
            self.listbox.insert('end', x)
            self.listbox2.insert('end', x)
            self.listbox3.insert('end', x)
            self.listbox4.insert('end', x)

        self.scrollb = Scrollbar(fileView, command=self.listbox.yview)
        self.scrollb.config(command=self.yview)
        self.scrollb.grid(row=1, column=4, sticky='nsew')

        self.showAlarmsB = Button(fileView, command=self.showAlarms, text="Show Alarms", width=30, padx=10, pady=4)
        self.showAlarmsB.grid(row=3, column=0, sticky="nsw", columnspan=2)

        self.optionalPropsB = Button(fileView, command=self.optionalProps, text="Extract Optional Props", width=30, padx=10, pady=4)
        self.optionalPropsB.grid(row=3, column=2, sticky="nse", columnspan=2)

        self.label = Label(fileView, text="Log Panel")
        self.label.grid(row=5, column=0, sticky="nsew", columnspan=4)

        logPanel = Frame(root, width=200, height=100)
        logPanel.pack(fill="both", expand=True)
        logPanel.grid_propagate(False)
        logPanel.grid_rowconfigure(0, weight=1)
        logPanel.grid_columnconfigure(0, weight=1)

        self.txt = Text(logPanel, borderwidth=3, relief="sunken")
        self.txt.configure(state="disabled")
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.clearB = Button(logPanel, command=self.clearLog, text="Clear Log", width=20)
        self.clearB.grid(row=1, column=0, sticky="nsw")

        scrollbar = Scrollbar(logPanel, command=self.txt.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollbar.set

    def logPrint(self, text):
        self.txt.configure(state="normal")
        self.txt.insert(END, text)
        self.txt.see(END)
        self.txt.insert(END, "\n")
        self.txt.update_idletasks()
        self.txt.configure(state="disabled")

    def clearLog(self):
        self.txt.configure(state="normal")
        self.txt.delete('1.0', END)
        self.txt.update_idletasks()
        self.txt.configure(state="disabled")

    def yscroll1(self, *args):
        if self.listbox2.yview() != self.listbox.yview():
            self.listbox2.yview_moveto(args[0])
            self.listbox3.yview_moveto(args[0])
            self.listbox4.yview_moveto(args[0])
            self.scrollb.set(*args)

    def yscroll2(self, *args):
        if self.listbox2.yview() != self.listbox.yview():
            self.listbox.yview_moveto(args[0])
            self.listbox3.yview_moveto(args[0])
            self.listbox4.yview_moveto(args[0])
            self.scrollb.set(*args)

    def yscroll3(self, *args):
        if self.listbox3.yview() != self.listbox.yview():
            self.listbox.yview_moveto(args[0])
            self.listbox2.yview_moveto(args[0])
            self.listbox4.yview_moveto(args[0])
            self.scrollb.set(*args)

    def yscroll4(self, *args):
        if self.listbox4.yview() != self.listbox.yview():
            self.listbox.yview_moveto(args[0])
            self.listbox2.yview_moveto(args[0])
            self.listbox3.yview_moveto(args[0])
            self.scrollb.set(*args)

    def yview(self, *args):
        self.listbox.yview(*args)
        self.listbox2.yview(*args)
        self.listbox3.yview(*args)
        self.listbox4.yview(*args)

    def open(self, *other):
        dirname = getcwd()
        path = askopenfilename(initialdir=dirname, title="Select file", filetypes=(("iCalendar", "*.ics"),("All files", "*.*")))
        rootDir, filename = os.path.split(path)
        if filename:
            #try:
            self.master.title(filename)
            self.openFile = path
                #display file in file view panel
            self.displayFileView()
                #display creation status in log window
            self.logPrint('opening file... ' + filename)
            #except:
                #display error in log window
				#self.logPrint("Error loading file")
            #return

    def save(self, *other):
        self.logPrint('save')
        #if its a new file
        filename = asksaveasfilename(initialdir="/", title="Select file",
                                     filetypes=(("iCalendar", "*.ics"), ("All files", "*.*")))
        if filename:
            try:
                self.logPrint(text=("File Saved to: %s", filename))
            except:
                #display error in log window
                self.logPrint("Error loading file")
            return

        #else just save

    def saveAs(self, *other):
        self.logPrint('save as')
        filename = asksaveasfilename(initialdir="/", title="Select file",
                                     filetypes=(("iCalendar", "*.ics"), ("All files", "*.*")))
        if filename:
            try:
                self.logPrint(text=("File Saved to: %s", filename))
            except:
                #display error in log window
                self.logPrint("Error loading file")
            return
        #on Ok
        self.master.title(filename)
        #on other do not modify

    def exit(self, *other):
        if messagebox.askyesno("Quit?", "Are you sure you want to quit?"):
            exit()

    def showAlarms(self):
        self.logPrint('show alarms')
        return

    def optionalProps(self):
        self.logPrint('show optional props')
        return

    def createCal(self):
        self.logPrint('createCal')

        prodID = simpledialog.askstring("Enter the prodID", "Enter the prodID").encode('utf-8')
        UID = simpledialog.askstring("Enter the UID", "Enter the UID").encode('utf-8')
        startDateTime = simpledialog.askstring("Enter the startDateTime", "Enter the startDateTime").encode('utf-8')
        action = simpledialog.askstring("Enter the action", "Enter the action").encode('utf-8')
        trigger = simpledialog.askstring("Enter the trigger", "Enter the trigger").encode('utf-8')

        now = datetime.now()
        date = now.strftime('%Y%m%d')
        time = now.microsecond
        creationDateTime = date + 'T' + str(time) + 'Z'
        b_creationDateTime = creationDateTime.encode('utf-8')

        testArr =((c_char * 1000) * 7)()

        testArr[0].value = b"2.0"
        testArr[1].value = prodID
        testArr[2].value = UID
        testArr[3].value = b_creationDateTime
        testArr[4].value = startDateTime
        testArr[5].value = action
        testArr[6].value = trigger 

        #if valid
        createSimpleCal = self.callib.createSimpleCalendar
        createSimpleCal.argtypes = [(c_char * 1000) * 7]
        createSimpleCal.restype = POINTER(Calendar)

        newCalPtr = createSimpleCal(testArr)

        newCalStr = self.printCal(newCalPtr)
        self.logPrint(newCalStr.decode("ISO-8859-1"))
        
        messagebox.showinfo("Important", "Reminder this Calendar has no Events. You must create events using the <create event> option in the menu")

        #self.logPrint(logtext)

    def createEvt(self):
        self.logPrint('createEvt')

        UID = simpledialog.askstring("Enter the UID", "Enter the UID")
        startDateTime = simpledialog.askstring("Enter the startDateTime", "Enter the startDateTime")
        now = datetime.now()
        date = now.strftime('%Y%m%d')
        time = now.microsecond
        DT = date + 'T' + str(time) + 'Z'

        self.logPrint(DT)

    def about(self):

        ABOUT_TEXT = """About

Asignemnt #3: iCalendar Editer
Creator: Greg Hetherington
Date: November, 16th, 2017"""

        DISCLAIMER = """Compatibllity

iCalendar V2.0"""

        toplevel = Toplevel()
        label1 = Label(toplevel, text=ABOUT_TEXT, height=0, width=50)
        label1.pack()
        label2 = Label(toplevel, text=DISCLAIMER, height=0, width=50)
        label2.pack()

root = Tk()
root.geometry("700x600")
app = Window(master=root)
root.mainloop()
