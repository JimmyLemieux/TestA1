#import the library
from ctypes import *

#we save the path to the library into a string, since we might need to access it more than once
testLibPath = './testlib.so'

#create a reference to the library module
testlib = CDLL(testLibPath)

#call a function from the module
testlib.myprint()

#pass a string to a C library as an argument:

#declare Python string
testStr = 'I am some string'

#encode it as an 8-bit ASCII (UTF-8) string - Python strings support Unicode by defult, and individual charms might be more than 8 bits in length
fStr = testStr.encode('utf-8')

#call the retval() function and pass it a Pythoon string converted to C string
len = testlib.retval(c_char_p(fStr))

#return the result
print('foo: ',len)

#if we know we're goign to call the function multiple times, we can make it more user friendly:

#create a new function name that points to the same function: 
calcLen = testlib.retval

#setup the types for calcLen()
#this is unnecessary, but will help
calcLen.argtypes = [c_char_p] #the input argument array contains one type - a C pointer to char
calcLen.restype = c_int

#create a helper function for converting a regular Python string to a C string - i.e. a pointer to char
def makeCString(str):
    utf8Str = str.encode('utf-8')
    cStr = c_char_p(utf8Str) #c_char_p() is a Ctypes function for createing a value of type c_char_p
    return cStr

tmpStr = makeCString("Hello, I'm, like, totally a C string.  And stuff.")
val = calcLen(tmpStr)
print(val)

