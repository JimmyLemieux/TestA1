from ctypes import *

#Create a Calentar type that matches our type in CalendarParser.h
class Calendar(Structure):
    _fields_ = [
        ("version", c_float),
        ("prodID", c_byte * 1000),
        ("events", c_void_p),
        ("properties", c_void_p)]

#save the path
calLibPath = 'icallib.so'

#load the module
callib = CDLL(calLibPath)

#create a sample file argument
filename = 'testCalSimpleUTC.ics'
fStr = filename.encode('utf-8')

#create an alias for callib.createCalendar() 
createCal = callib.createCalendar

# Help the Python compiler figure out the types for the function  
#********** these can be commented out - Python can infer them **********
createCal.argtypes = [c_char_p,POINTER(POINTER(Calendar))]
createCal.restype = c_int
#**********************************************************************


#create an alias for callib.printCalendar() 
printCal = callib.printCalendar

# Help the Python compiler figure out the types for the function  
printCal.argtypes = [POINTER(Calendar)] #this can also be commented out
printCal.restype = c_char_p             #this CANNOT be commented out! Otherwise Python will decide that printCal returns an int!

# create a variable that will store the pointer to the calendar
# if we don't do this, Python will be unhappy
calPtr = POINTER(Calendar)()

#call the library function createCalendar() using our alias createCal
print('returned = ',createCal(fStr,byref(calPtr))) #notice the type

#we need to dereference calPtr - which is a pointer to Calendar object
#the .contents property of a pointer returns the thing it points to
testCal = calPtr.contents
print('version = ', testCal.version)

#testCal.prodID is an array of chars.  First we convert it to a char pointer
stuff = cast(testCal.prodID, c_char_p)

#Then we decode (convert) the char pointer to a Python string
print('',stuff.value.decode("utf-8"))

#call printCal
calStr = printCal(calPtr)

#and display the result
print(calStr.decode("utf-8"))

#We want to create a new calendar.  Doing so by hand from Python is painful
#Instead we create a C function that does it for us - a constructor, as it were
#The best way to interface with a complex C struct is really to treat is an an object
#And manipulate it using "methods"

#The minimal calendar needs 4 strings
#passing an array of strings is kinda ugly, so we hack it together with a 4x1000 array
testArr =((c_char * 1000) * 4)()

#fill th array with _byte_ values
#the "b" prefix tells Python to treat the "string" as an array of bytes, instead of a Python string
testArr[0].value = b"2.0"
testArr[1].value = b"-//hacksw/handcal//NONSGML v1.0//EN"
testArr[2].value = b"uid2@examplezz.com"
testArr[3].value = b"20171026T165100Z"

#Create a reference to a library function and set up its types
createSimpleCal = CDLL(calLibPath).createSimpleCalendar
createSimpleCal.argtypes = [(c_char * 1000) * 4] #this can also be commented out
createSimpleCal.restype = POINTER(Calendar)      #again, this CANNOT be commented out! Otherwise Python will decide that createSimpleCal returns an int!

#create a new Calendar object
newCalPtr = createSimpleCal(testArr)

#Print it
newCalStr = printCal(newCalPtr)
print(newCalStr.decode("utf-8"))

#Setup the reference for...well, you get the idea
deleteCal = CDLL(calLibPath).deleteCalendar
deleteCal.argtypes = [POINTER(Calendar)]

#clean up after ourselves
deleteCal(newCalPtr)


