CC = gcc
CCFLAGS += -std=c11 -shared

testlib: testlib.c
	$(CC) $(CCFLAGS) -o testlib.so -fPIC testlib.c 
clean:
	rm -rf *.o *.so