from ctypes import *
from os import *
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *
from tkinter import simpledialog
from datetime import *
import mysql.connector
import sys

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
        self.setupSQL()
        self.init_window()
        self.previousIndex = -1;
        self.openFile = ""
        self.showRem = 0
        self.setupCal()
        
    def setupSQL(self):
        
        if len(sys.argv) >= 3:
            print("Too many arguments given, only give 1")
            exit()
        elif len(sys.argv) == 2:
            dbName = str(sys.argv[1])
            uName = dbName
            attempt = 0
            while attempt < 3:
                
                passwd = simpledialog.askstring("Password Prompt", "Enter Password: ")
                attempt = attempt + 1
                try:
                    self.conn = mysql.connector.connect(host="dursley.socs.uoguelph.ca",database=dbName,user=uName, password=passwd)
                    attempt = 0
                    break;
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
            if attempt != 0:
                exit()
        else:
            
            dbName = "ghetheri"
            uName = "ghetheri"  
            passwd = "0936504"
        
            try:
                self.conn = mysql.connector.connect(host="dursley.socs.uoguelph.ca",database=dbName,user=uName, password=passwd)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                exit()
        
        self.cursor = self.conn.cursor()
        
        createQuery="create table ORGANIZER (org_id int auto_increment, name char(60) not null, contact char(60) not null, primary key(org_id) )"
        #try:
            #self.cursor.execute(createQuery)
        #except mysql.connector.Error as err:
            #print("Something went wrong: {}".format(err))
        
        createQuery="create table EVENT (event_id int auto_increment, summary char(60) not null, start_time datetime not null, location char(60), organizer int, num_alarms int, primary key(event_id), foreign key(organizer) references ORGANIZER(org_id) ON DELETE CASCADE)"
        #try:
            #self.cursor.execute(createQuery)
        #except mysql.connector.Error as err:
            #print("Something went wrong: {}".format(err))
    
        
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
        
        self.orgForEvent = self.callib.getOrgForEvent
        self.orgForEvent.argtypes = [POINTER(Calendar), c_int]
        self.orgForEvent.restype = c_char_p
                
        self.locationForEvent = self.callib.getLocationForEvent
        self.locationForEvent.argtypes = [POINTER(Calendar), c_int]
        self.locationForEvent.restype = c_char_p
        
        self.datetimeForEvent = self.callib.getDatetimeForEvent
        self.datetimeForEvent.argtypes = [POINTER(Calendar), c_int]
        self.datetimeForEvent.restype = c_char_p
        
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
        
        self.database = Menu(menu, tearoff=0)
        self.database.add_command(label="Store All Events", command=self.storeAllEvents)
        self.database.add_command(label="Store Current Event", command=self.storeCurrentEvents)
        self.database.add_command(label="Clear All Data", command=self.clearAllData)
        self.database.add_command(label="Display DB status", command=self.displayDBStatus)
        self.database.add_command(label="Execute Query", command=self.executeQuery)

        menu.add_cascade(label="File", menu=file)
        menu.add_cascade(label="Create", menu=self.create)
        menu.add_cascade(label="Help", menu=help)
        menu.add_cascade(label="Database", menu=self.database)

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
            self.cursor.close()    
            self.conn.close()
            exit()
#DataBase methods
    def storeAllEvents(self):
        
        if self.calPtr:
            
            numOfEvents = self.numEvents(self.calPtr)
            for i in range(0, numOfEvents):
                orgInfo = self.orgForEvent(self.calPtr, i)
                pythOrg = orgInfo.decode("ISO-8859-1")
            
                orgSplit = pythOrg.split(":")
                name = orgSplit[1]
                email = orgSplit[3]
                
                sqlq = "SELECT COUNT(1) FROM ORGANIZER WHERE name = '" + name + "'"
                
                self.cursor.execute(sqlq)
                
                if self.cursor.fetchone()[0]:
                    self.cursor.execute("SELECT name, org_id FROM ORGANIZER")
                    result_set = self.cursor.fetchall()
                    for row in result_set:
                        if row[0] == name:
                            self.orgID = row[1]
                    
                else:
                    record = "INSERT INTO ORGANIZER VALUES (DEFAULT, '" + name + "', '" + email + "')"
                    try:
                        self.cursor.execute(record)
                    except mysql.connector.Error as err:
                        print("Something went wrong: {}".format(err))             
            
                    self.orgID = self.cursor.lastrowid
            
                location = self.locationForEvent(self.calPtr, i)
                summary = self.getEventSummary(self.calPtr, i)
                numAlarms = self.numAlarms(self.calPtr, i)
                datetime = self.datetimeForEvent(self.calPtr, i)
            
            
                record = "INSERT INTO EVENT(summary, start_time, location, organizer, num_alarms) VALUES ('" + summary.decode("ISO-8859-1") + "', STR_TO_DATE('" + datetime.decode("ISO-8859-1") + " 115959" + "', '%Y%m%d %h%i%s'), '" + location.decode("ISO-8859-1") + "', '" + str(self.orgID) + "', " + str(numAlarms) + ")"
                try:
                    self.cursor.execute(record)
                    self.conn.commit()
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
            
            
            self.displayDBStatus()
            
        else:
            self.logPrint("No Calendar Opened")
            

    def storeCurrentEvents(self):
        
        selection = self.listbox.curselection()
        if selection:
            orgInfo = self.orgForEvent(self.calPtr, selection[0])
            pythOrg = orgInfo.decode("ISO-8859-1")
            
            orgSplit = pythOrg.split(":")
            name = orgSplit[1]
            email = orgSplit[3]
            
            sqlq = "SELECT COUNT(1) FROM ORGANIZER WHERE name = '" + name + "'"
                
            self.cursor.execute(sqlq)
                
            if self.cursor.fetchone()[0]:
                self.cursor.execute("SELECT name, org_id FROM ORGANIZER")
                result_set = self.cursor.fetchall()
                for row in result_set:
                    if row[0] == name:
                        self.orgID = row[1]
                    
            else:
                record = "INSERT INTO ORGANIZER VALUES (DEFAULT, '" + name + "', '" + email + "')"
                try:
                    self.cursor.execute(record)
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))             
            
                self.orgID = self.cursor.lastrowid

            
            location = self.locationForEvent(self.calPtr, selection[0])
            summary = self.getEventSummary(self.calPtr, selection[0])
            numAlarms = self.numAlarms(self.calPtr, selection[0])
            datetime = self.datetimeForEvent(self.calPtr, selection[0])
            
            
            record = "INSERT INTO EVENT(summary, start_time, location, organizer, num_alarms) VALUES ('" + summary.decode("ISO-8859-1") + "', STR_TO_DATE('" + datetime.decode("ISO-8859-1") + " 115959" + "', '%Y%m%d %h%i%s'), '" + location.decode("ISO-8859-1") + "', '" + str(self.orgID) + "', " + str(numAlarms) + ")"
            try:
                self.cursor.execute(record)
                self.conn.commit()
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
            
            
            self.displayDBStatus()

        else:
            self.logPrint("No Event Selected")
                    
        return
    def clearAllData(self):
        try:
            self.cursor.execute("TRUNCATE TABLE EVENT")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            self.cursor.execute("TRUNCATE TABLE ORGANIZER")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        return
    def displayDBStatus(self):
            
        orgLen = 0
        evtLen = 0
            
        try:
            self.cursor.execute("SELECT * FROM ORGANIZER")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        rows = self.cursor.fetchall()
        
        for row in rows:
            orgLen = orgLen + 1
            
        try:
            self.cursor.execute("SELECT * FROM EVENT")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        rows = self.cursor.fetchall()
        
        for row in rows:
            evtLen = evtLen + 1
        
        self.logPrint("Database has " + str(orgLen) + " organizers and " + str(evtLen) + " events")

        
    def executeQuery(self):
        
        toplevel = Toplevel()
        queryPanel = Frame(toplevel, width=200, height=300)
        queryPanel.pack(fill="both", expand=True)
        queryPanel.grid_rowconfigure(0, weight=1)
        queryPanel.grid_rowconfigure(1, weight=1)
        queryPanel.grid_rowconfigure(2, weight=1)
        queryPanel.grid_rowconfigure(3, weight=1)
        queryPanel.grid_rowconfigure(4, weight=1)
        queryPanel.grid_rowconfigure(5, weight=1)
        queryPanel.grid_rowconfigure(6, weight=1)
        queryPanel.grid_rowconfigure(7, weight=1)
        queryPanel.grid_rowconfigure(8, weight=1)

        queryPanel.grid_columnconfigure(0, weight=1)
        queryPanel.grid_columnconfigure(1, weight=1)
        queryPanel.grid_columnconfigure(2, weight=1)
        queryPanel.grid_columnconfigure(3, weight=1)
        queryPanel.grid_columnconfigure(4, weight=1)
        self.v = IntVar()
        
        self.label = Label(queryPanel, text="Query:")
        self.label.grid(row=0, column=0, sticky="nsw")
        
        labelv = Label(queryPanel, text="Variables:")
        labelv.grid(row=0, column=1, sticky="nsew", columnspan=3)
        
        option1 = Radiobutton(queryPanel, text="Display all events sorted by start date", variable=self.v, value=1)
        option1.grid(row=1, column=0, sticky="nsw")
        
        option2 = Radiobutton(queryPanel, text="Display the events from a specific organizer", variable=self.v, value=2)
        option2.grid(row=2, column=0, sticky="nsw")
        
        label2 = Label(queryPanel, text="Organizer name:")
        label2.grid(row=2, column=2, sticky="nse")
        
        self.opt2Org = Entry(queryPanel)
        self.opt2Org.grid(row=2, column=3, sticky="nsew")
        
        option3 = Radiobutton(queryPanel, text="Display number of events and list them at a specific Location", variable=self.v, value=3)
        option3.grid(row=3, column=0, sticky="nsw")
        
        label3 = Label(queryPanel, text="Location:")
        label3.grid(row=3, column=2, sticky="nse")
        
        self.opt3Evt = Entry(queryPanel)
        self.opt3Evt.grid(row=3, column=3, sticky="nsew")
        
        option4 = Radiobutton(queryPanel, text="Contact Organizer", variable=self.v, value=4)
        option4.grid(row=4, column=0, sticky="nsw")
        
        label4 = Label(queryPanel, text="Event ID:")
        label4.grid(row=4, column=2, sticky="nse")
        
        self.opt4Evt = Entry(queryPanel)
        self.opt4Evt.grid(row=4, column=3, sticky="nsew")
        
        option5 = Radiobutton(queryPanel, text="List all Events with at least N alarms", variable=self.v, value=5)
        option5.grid(row=5, column=0, sticky="nsw")
        
        label4 = Label(queryPanel, text="N = ")
        label4.grid(row=5, column=2, sticky="nse")
        
        self.opt5Evt = Entry(queryPanel)
        self.opt5Evt.grid(row=5, column=3, sticky="nsew")
        
        option6 = Radiobutton(queryPanel, text="Custom SQL statement", variable=self.v, value=0)
        option6.grid(row=6, column=0, sticky="nsw")
        
        self.selectTxt = Entry(queryPanel)
        self.selectTxt.insert(END, 'SELECT')
        self.selectTxt.grid(row=6, column=1, sticky="nsew", columnspan=5)
        
        submitB = Button(queryPanel, command=self.submit, text="Submit", width=20, padx=20, pady=10)
        submitB.grid(row=7, column=0, sticky="nsw", columnspan=1)

        helpB = Button(queryPanel, command=self.help, text="Help", width=20, padx=20, pady=10)
        helpB.grid(row=7, column=4, sticky="nse", columnspan=1)
        
        self.label = Label(queryPanel, text="Results")
        self.label.grid(row=8, column=0, sticky="nsew", columnspan=5)
        
        resultPanel = Frame(toplevel, width=200, height=200)
        resultPanel.pack(fill="both", expand=True)
        resultPanel.grid_propagate(False)
        resultPanel.grid_rowconfigure(0, weight=1)
        resultPanel.grid_columnconfigure(0, weight=1)

        self.DBtxt = Text(resultPanel, borderwidth=3, relief="sunken")
        self.DBtxt.configure(state="disabled")
        self.DBtxt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.DBclearB = Button(resultPanel, command=self.clearResults, text="Clear Results", width=20)
        self.DBclearB.grid(row=1, column=0, sticky="nsw")

        scrollbar = Scrollbar(resultPanel, command=self.DBtxt.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        self.DBtxt['yscrollcommand'] = scrollbar.set        
        
        toplevel.focus_force()
        
        return
    def submit(self, *other):
        
        returnInt = self.v.get()
        
        if returnInt == 0:
            query = self.selectTxt.get()
        elif returnInt == 1:
            query = "SELECT * FROM EVENT ORDER BY start_time"
        elif returnInt == 2:
            if self.opt2Org.get() != "":
                name = self.opt2Org.get()
                self.cursor.execute("SELECT a.event_id, a.summary, a.organizer, a.start_time, b.name FROM EVENT a, ORGANIZER b WHERE a.organizer = b.org_id")
                result_set = self.cursor.fetchall()
                for row in result_set:
                    if str(row[4]) == name:
                        self.resultsPrint("Event_id:" + str(row[0]) + "| Summary:" + str(row[1]) + "| Start_time:" + str(row[3]))
            else:
                self.resultsPrint("No Organizer listed")
        elif returnInt == 3:
            if self.opt3Evt.get() != "":
                loc = self.opt3Evt.get()
                self.cursor.execute("SELECT event_id, summary, start_time, location FROM EVENT")
                result_set = self.cursor.fetchall()
                x = 0
                for row in result_set:
                    if str(row[3]) == loc:
                        x = x + 1
                        self.resultsPrint("Event_id:" + str(row[0]) + "| Summary:" + str(row[1]) + "| Start_time:" + str(row[2]))
                self.resultsPrint("Number of Events: " + str(x))
            else:
                self.resultsPrint("No Location listed")
        elif returnInt == 4:
            if self.opt4Evt.get() != "":
                evtID = self.opt4Evt.get()
                self.cursor.execute("SELECT a.event_id, a.organizer, b.name, b.contact FROM EVENT a, ORGANIZER b WHERE a.organizer = b.org_id")
                result_set = self.cursor.fetchall()
                for row in result_set:
                    if str(row[0]) == evtID:
                        self.resultsPrint("Org_id:" + str(row[1]) + "| Org Name:" + str(row[2]) + "| Org Contact:" + str(row[3]))
            else:
                self.resultsPrint("No Event listed")
        elif returnInt == 5:
            if self.opt5Evt.get() != "":
                numAlarms = self.opt5Evt.get()
                self.cursor.execute("SELECT num_alarms, event_id, summary FROM EVENT WHERE num_alarms >= " + numAlarms + " ORDER BY num_alarms ASC")
                result_set = self.cursor.fetchall()
                for row in result_set:
                    self.resultsPrint("Event_id:" + str(row[1]) + "| Summary:" + str(row[2]) + "| Num_alarms:" + str(row[0]))
            else:
                self.resultsPrint("No N listed")
            
        if returnInt < 2:
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                self.resultsPrint("Invalid Query")
                print("Something went wrong: {}".format(err))
 
            result_set = self.cursor.fetchall()
            for row in result_set:
                self.resultsPrint("Event_id:" + str(row[0]) + "| Summary:" + str(row[1]) + "| Start_time:" + str(row[2]) + "| Location:" + str(row[3]) + "| Organizer_id:" + str(row[4]) + "| Num_alarms:" + str(row[5]))
            
        return
    def help(self):
        toplevel = Toplevel()
        helpPanel = Frame(toplevel)
        helpPanel.pack(fill="both", expand=True)
        helpPanel.grid_rowconfigure(0, weight=1)
        helpPanel.grid_rowconfigure(1, weight=1)
        helpPanel.grid_rowconfigure(2, weight=1)
        helpPanel.grid_rowconfigure(3, weight=1)

        helpPanel.grid_columnconfigure(0, weight=1)
        helpPanel.grid_columnconfigure(1, weight=1)
        helpPanel.grid_columnconfigure(2, weight=1)
        helpPanel.grid_columnconfigure(3, weight=1)
        
        txtH = Text(helpPanel, borderwidth=3, relief="sunken")
        
        try:
            self.cursor.execute("DESCRIBE ORGANIZER")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        txtH.insert(END, "ORGANIZER:\n")
        for column in self.cursor.fetchall():
            txtH.insert(END, column)
            txtH.see(END)
            txtH.insert(END, "\n")
        
        try:
            self.cursor.execute("DESCRIBE EVENT")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        txtH.insert(END, "\nEvent:\n")
        for column in self.cursor.fetchall():
            txtH.insert(END, column)
            txtH.see(END)
            txtH.insert(END, "\n")
            
        txtH.configure(state="disabled")
        txtH.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
    def resultsPrint(self, text):
        self.DBtxt.configure(state="normal")
        self.DBtxt.insert(END, text)
        self.DBtxt.see(END)
        self.DBtxt.insert(END, "\n")
        self.DBtxt.update_idletasks()
        self.DBtxt.configure(state="disabled")
        
    def clearResults(self):
       self.DBtxt.configure(state="normal")
       self.DBtxt.delete('1.0', END)
       self.DBtxt.update_idletasks()
       self.DBtxt.configure(state="disabled")
        
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
