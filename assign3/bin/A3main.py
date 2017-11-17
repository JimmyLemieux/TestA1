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
        self.showRem = 0
        self.setupCal()

    def setupCal(self):
        calLibPath = './bin/icallib.so'
        self.callib = CDLL(calLibPath)
        
        self.calPtr = None

        self.createCal = self.callib.createCalendar
        self.createCal.argtypes = [c_char_p,POINTER(POINTER(Calendar))]
        self.createCal.restype = c_int
        
        self.validCal = self.callib.validateCalendar
        self.validCal.argtypes = [POINTER(Calendar)]
        self.validCal.restype = c_int
        
        self.writeCal = self.callib.writeCalendar
        self.writeCal.argtypes = [c_char_p, POINTER(Calendar)]
        self.writeCal.restype = c_int

        self.printCal = self.callib.printCalendar
        self.printCal.restype = c_char_p
        
        self.numEvents = self.callib.getNumOfEvents
        self.numEvents.argtypes = [POINTER(Calendar)]
        self.numEvents.restype = c_int
        
        self.numProps = self.callib.getNumOfProps
        self.numProps.argtypes = [POINTER(Calendar), c_int]
        self.numProps.restype = c_int
        
        self.numAlarms = self.callib.getNumOfAlarms
        self.numAlarms.argtypes = [POINTER(Calendar), c_int]
        self.numAlarms.restype = c_int
        
        self.getEventSummary = self.callib.getSummary
        self.getEventSummary.argtypes = [POINTER(Calendar), c_int]
        self.getEventSummary.restype = c_char_p
        
        self.printAlarmsForEv = self.callib.printAlarmsForEvent
        self.printAlarmsForEv.argtypes = [POINTER(Calendar), c_int]
        self.printAlarmsForEv.restype = c_char_p
        
        self.printPropsForEv = self.callib.printPropsForEvent
        self.printPropsForEv.argtypes = [POINTER(Calendar), c_int]
        self.printPropsForEv.restype = c_char_p
        
    def displayFileView(self):
        self.create.entryconfig("Create event", state="normal")
        self.create.entryconfig("Create alarm", state="normal")
        self.listbox.delete(0, END)
        self.listbox2.delete(0, END)
        self.listbox3.delete(0, END)
        self.listbox4.delete(0, END)

        numOfEvents = self.numEvents(self.calPtr)
        for x in range(0, numOfEvents):
            self.listbox.insert('end', x+1)
            numOfProps = self.numProps(self.calPtr, x)
            self.listbox2.insert('end', numOfProps)
            numOfAlarms = self.numAlarms(self.calPtr, x)
            self.listbox3.insert('end', numOfAlarms)
            summary = self.getEventSummary(self.calPtr, x)
            self.listbox4.insert('end', summary.decode("ISO-8859-1"))
            

    def init_window(self):
        self.master.title("iCalGUI")
        self.pack(fill=BOTH, expand=1)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        file = Menu(menu, tearoff=0)
        file.add_command(label="Open...", command=self.open, accelerator="Ctrl+O")
        file.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file.add_command(label="Save as...", command=self.saveAs, accelerator="Ctrl+Z")
        file.add_command(label="Exit", command=self.exit, accelerator="Ctrl+X")
        root.bind('<Control-o>', self.open)
        root.bind('<Control-s>', self.save)
        root.bind('<Control-z>', self.saveAs)
        root.bind('<Control-x>', self.exit)
        root.bind('<Escape>', self.exit)
        root.protocol("WM_DELETE_WINDOW", self.exit)

        self.create = Menu(menu, tearoff=0)
        self.create.add_command(label="Create calendar", command=self.createCal)
        self.create.add_command(label="Create event", command=self.createEvt, state="disabled")#state="disabled" at start and set to normal if a calendar is in use
        self.create.add_command(label="Create alarm", command=self.addAlarm, state="disabled")#state="disabled" at start and set to normal if a calendar is in use


        help = Menu(menu, tearoff=0)
        help.add_command(label="About iCalGUI...", command=self.about)

        menu.add_cascade(label="File", menu=file)
        menu.add_cascade(label="Create", menu=self.create)
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

        self.label = Label(fileView, text="Properties", relief="sunken")
        self.label.grid(row=0, column=1, sticky="sew")

        self.label = Label(fileView, text="Alarms", relief="sunken")
        self.label.grid(row=0, column=2, sticky="sew")

        self.label = Label(fileView, width=50, text="Summary", relief="sunken")
        self.label.grid(row=0, column=3, sticky="sew")

        self.listbox = Listbox(fileView, height=15, exportselection=0, yscrollcommand=self.yscroll1)
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

        self.scrollb = Scrollbar(fileView, command=self.listbox.yview)
        self.scrollb.config(command=self.yview)
        self.scrollb.grid(row=1, column=5, sticky='nsew')

        self.showAlarmsB = Button(fileView, command=self.showAlarms, text="Show Alarms", width=20, padx=20, pady=10)
        self.showAlarmsB.grid(row=3, column=0, sticky="nsw", columnspan=2)

        self.optionalPropsB = Button(fileView, command=self.optionalProps, text="Extract Optional Properties", width=20, padx=20, pady=10)
        self.optionalPropsB.grid(row=3, column=2, sticky="nse", columnspan=3)

        self.label = Label(fileView, text="Log Panel")
        self.label.grid(row=5, column=0, sticky="nsew", columnspan=4)

        logPanel = Frame(root, width=200, height=300)
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
        if path:
            try:
                rootDir, filename = os.path.split(path)
                tempCalPtr = POINTER(Calendar)()
                fStr = path.encode('utf-8')
                errNum = self.createCal(fStr, byref(tempCalPtr))
                errCode = self.validCal(tempCalPtr)
                if errNum == 0 and errCode == 0:
                    #display file in file view panel
                    self.logPrint('opening file... ' + filename)
                    self.master.title(filename)
                    self.openFile = path
                    self.calPtr = POINTER(Calendar)()
                    self.calPtr = tempCalPtr
                    self.displayFileView()

                else:
                    if errCode == 1 or errNum == 1:
                        Ereturn = "INV_FILE"
                    elif errCode == 2:
                        Ereturn = "INV_CAL"
                    elif errCode == 3:
                        Ereturn = "INV_VER"
                    elif errCode == 5:
                        Ereturn = "INV_PRODID"
                    elif errCode == 4:
                        Ereturn = "DUP_VER"
                    elif errCode == 6:
                        Ereturn = "DUP_PRODID"
                    elif errCode == 7:
                        Ereturn = "INV_EVENT"
                    elif errCode == 8:
                        Ereturn = "INV_CREATEDT"
                    elif errCode == 9:
                        Ereturn = "INV_ALARM"
                    else:
                        Ereturn = "OTHER_ERROR"
                    self.logPrint("Invalid Calendar Can't Open: ErrorCode = " + Ereturn)

            except:
                #display error in log window
                self.logPrint("Error loading file: Crash")
            return

    def save(self, *other):
        if self.showRem == 1:
            messagebox.showinfo("Important", "Reminder this Calendar has no Events. You must create events using the <create event> option in the menu")

        errCode = self.validCal(self.calPtr)
        if self.openFile and errCode == 0:
            rootDir, filename = os.path.split(self.openFile)
            if filename:
                try:
                    errWrite = self.writeCal(filename.encode('ISO-8859-1'), self.calPtr)
                    if errWrite != 0:
                        global Ereturn
                        
                        if errCode == 1:
                            Ereturn = "INV_FILE"
                        elif errCode == 2:
                            Ereturn = "INV_CAL"
                        elif errCode == 3:
                            Ereturn = "INV_VER"
                        elif errCode == 5:
                            Ereturn = "INV_PRODID"
                        elif errCode == 4:
                            Ereturn = "DUP_VER"
                        elif errCode == 6:
                            Ereturn = "DUP_PRODID"
                        elif errCode == 7:
                            Ereturn = "INV_EVENT"
                        elif errCode == 8:
                            Ereturn = "INV_CREATEDT"
                        elif errCode == 9:
                            Ereturn = "INV_ALARM"
                        else:
                            Ereturn = "OTHER_ERROR"
                        self.logPrint("Can't Save: ErrorCode = " + Ereturn + " While writing to: " + filename)
                    else:
                        self.master.title(filename)
                        self.logPrint(text=("File Saved to: " + filename))
                except:
                    self.logPrint("Error Saveing file: Crash")
                return
        elif errCode == 0:
            self.saveAs()
        else:
            
            if errCode == 0:
                self.calPtr = newCalPtr
                self.displayFileView()
            elif errCode == 1:
                Ereturn = "INV_FILE"
            elif errCode == 2:
                Ereturn = "INV_CAL"
            elif errCode == 3:
                Ereturn = "INV_VER"
            elif errCode == 5:
                Ereturn = "INV_PRODID"
            elif errCode == 4:
                Ereturn = "DUP_VER"
            elif errCode == 6:
                Ereturn = "DUP_PRODID"
            elif errCode == 7:
                Ereturn = "INV_EVENT"
            elif errCode == 8:
                Ereturn = "INV_CREATEDT"
            elif errCode == 9:
                Ereturn = "INV_ALARM"
            else:
                Ereturn = "OTHER_ERROR"
            self.logPrint("Invalid Calendar Can't Save: ErrorCode = " + Ereturn)

    def saveAs(self, *other):
        if self.showRem == 1:
            messagebox.showinfo("Important", "Reminder this Calendar has no Events. You must create events using the <create event> option in the menu")

        errCode = self.validCal(self.calPtr)
        if errCode == 0:
        
            dirname = getcwd()
            path = asksaveasfilename(initialdir=dirname, title="Select file",
                                     filetypes=(("iCalendar", "*.ics"), ("All files", "*.*")))
            rootDir, filename = os.path.split(path)
            if filename:
                try:
                    errWrite = self.writeCal(filename.encode('ISO-8859-1'), self.calPtr)
                    if errWrite != 0:
                        self.logPrint(text=("File Errored while writing to: " + filename))
                    else:
                        self.master.title(filename)
                        self.logPrint(text=("File Saved to: " + filename))
                except:
                    self.logPrint("Error loading file")
                return
        else:
            #on other do not modify
            global Ereturn
            
            if errCode == 0:
                self.calPtr = newCalPtr
                self.displayFileView()
            elif errCode == 1:
                Ereturn = "INV_FILE"
            elif errCode == 2:
                Ereturn = "INV_CAL"
            elif errCode == 3:
                Ereturn = "INV_VER"
            elif errCode == 5:
                Ereturn = "INV_PRODID"
            elif errCode == 4:
                Ereturn = "DUP_VER"
            elif errCode == 6:
                Ereturn = "DUP_PRODID"
            elif errCode == 7:
                Ereturn = "INV_EVENT"
            elif errCode == 8:
                Ereturn = "INV_CREATEDT"
            elif errCode == 9:
                Ereturn = "INV_ALARM"
            else:
                Ereturn = "OTHER_ERROR"
            self.logPrint("Invalid Calendar Can't Save: ErrorCode = " + Ereturn)


    def exit(self, *other):
        if messagebox.askyesno("Quit?", "Are you sure you want to quit?"):
            exit()

    def showAlarms(self):
        selection = self.listbox.curselection()
        if selection:
            alarms = self.printAlarmsForEv(self.calPtr, selection[0])
            self.logPrint(alarms.decode("ISO-8859-1"))
        else:
            self.logPrint("No Event Selected")

    def optionalProps(self):
        selection = self.listbox.curselection()
        if selection:
            props = self.printPropsForEv(self.calPtr, selection[0])
            self.logPrint(props.decode("ISO-8859-1"))
        else:
            self.logPrint("No Event Selected")
            
    def addAlarm(self):
        selection = self.listbox.curselection()
        if selection:
            self.createAlm(selection[0])
        else:
            self.logPrint("No Event Selected")

    def createCal(self):
        self.openFile = None
        self.master.title("iCalGUI")
        self.calPtr = POINTER(Calendar)()

        prodID = simpledialog.askstring("Enter the prodID", "Enter the prodID")
        
        #UID = simpledialog.askstring("Enter the UID", "Enter the UID").encode('ISO-8859-1')

        #now = datetime.now()
        #date = now.strftime('%Y%m%d')
        #time = now.strftime('%H%M%S')
        #creationDateTime = date + 'T' + str(time)
        #b_creationDateTime = creationDateTime.encode('ISO-8859-1')

        #testArr =((c_char * 1000) * 1)()

        #testArr[0].value = prodIDc
        #testArr[1].value = UID
        #testArr[2].value = b_creationDateTime

        #ifvalid
        if prodID != "" and prodID != None:
            prodIDc = prodID.encode('ISO-8859-1')
            testArr =((c_char * 1000) * 1)()
            testArr[0].value = prodIDc
            createSimpleCal = self.callib.createSimpleCalendar
            createSimpleCal.argtypes = [(c_char * 1000) * 1]
            createSimpleCal.restype = POINTER(Calendar)

            newCalPtr = POINTER(Calendar)()
            newCalPtr = createSimpleCal(testArr)
        
            self.calPtr = newCalPtr
            self.displayFileView()
            
            self.showRem = 1
            self.logPrint("Calendar Created")
            messagebox.showinfo("Important", "Reminder this Calendar has no Events. You must create events using the <create event> option in the menu")
        else:
            self.logPrint("Invailid Calendar prodID must exist")


    def createEvt(self):
        UID = simpledialog.askstring("Enter the UID", "Enter the UID").encode('ISO-8859-1')
        startDateTime = simpledialog.askstring("Enter the startDateTime", "Enter the startDateTime").encode('ISO-8859-1')
        #endDateTime = simpledialog.askstring("Enter the endDateTime", "Enter the endDateTime").encode('ISO-8859-1')
        
        now = datetime.now()
        date = now.strftime('%Y%m%d')
        time = now.strftime('%H%M%S')
        DT = date + 'T' + time
        b_creationDateTime = DT.encode('ISO-8859-1')

        testArr =((c_char * 1000) * 3)()

        testArr[0].value = UID
        testArr[1].value = startDateTime
        testArr[2].value = b_creationDateTime
        #testArr[3].value = endDateTime

        createSimpleEvent = self.callib.createEvent
        createSimpleEvent.argtypes = [POINTER(Calendar), (c_char * 1000) * 3]
        createSimpleEvent.restype = POINTER(Calendar)

        newCalPtr = createSimpleEvent(self.calPtr, testArr)
        
        global Ereturn
        
        errCode = self.validCal(newCalPtr)
        if errCode == 0:
            self.logPrint("Event Created")
            self.calPtr = newCalPtr
            self.displayFileView()
            self.showRem = 0
        elif errCode == 1:
            Ereturn = "INV_FILE"
        elif errCode == 2:
            Ereturn = "INV_CAL"
        elif errCode == 3:
            Ereturn = "INV_VER"
        elif errCode == 5:
            Ereturn = "INV_PRODID"
        elif errCode == 4:
            Ereturn = "DUP_VER"
        elif errCode == 6:
            Ereturn = "DUP_PRODID"
        elif errCode == 7:
            Ereturn = "INV_EVENT"
        elif errCode == 8:
            Ereturn = "INV_CREATEDT"
        elif errCode == 9:
            Ereturn = "INV_ALARM"
        else:
            Ereturn = "OTHER_ERROR"
            
        if errCode != 0:
            self.logPrint("Invalid Calendar: ErrorCode = " + Ereturn)
                    
    def createAlm(self, event):
        action = simpledialog.askstring("Enter the Action", "Enter the Action").encode('ISO-8859-1')
        trigger = simpledialog.askstring("Enter the Trigger", "Enter the Trigger").encode('ISO-8859-1')

        testArr =((c_char * 1000) * 2)()

        testArr[0].value = action
        testArr[1].value = trigger

        createSimpleAlarm = self.callib.createAlarm
        createSimpleAlarm.argtypes = [POINTER(Calendar), (c_char * 1000) * 2, c_int]
        createSimpleAlarm.restype = POINTER(Calendar)

        newCalPtr = createSimpleAlarm(self.calPtr, testArr, event)
        
        global Ereturn
        
        errCode = self.validCal(newCalPtr)
        if errCode == 0:
            self.logPrint("Alarm Created")
            self.calPtr = newCalPtr
            self.displayFileView()
            self.showRem = 0
        elif errCode == 1:
            Ereturn = "INV_FILE"
        elif errCode == 2:
            Ereturn = "INV_CAL"
        elif errCode == 3:
            Ereturn = "INV_VER"
        elif errCode == 5:
            Ereturn = "INV_PRODID"
        elif errCode == 4:
            Ereturn = "DUP_VER"
        elif errCode == 6:
            Ereturn = "DUP_PRODID"
        elif errCode == 7:
            Ereturn = "INV_EVENT"
        elif errCode == 8:
            Ereturn = "INV_CREATEDT"
        elif errCode == 9:
            Ereturn = "INV_ALARM"
        else:
            Ereturn = "OTHER_ERROR"
            
        if errCode != 0:
            self.logPrint("Invalid Calendar: ErrorCode = " + Ereturn)
                    
    def about(self):

        ABOUT_TEXT = """About

Asignemnt #3: iCalendar Editor
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
root.geometry("700x580")
app = Window(master=root)
root.mainloop()
