all: list parser pyth

list: src/LinkedListAPI.c

	gcc src/LinkedListAPI.c -Iinclude -std=c11 -fPIC -o bin/LinkedListAPI.o -c

	ar cr bin/libllist.a bin/LinkedListAPI.o

parser: src/CalendarParser.c

	gcc src/CalendarParser.c -Iinclude -std=c11 -fPIC -o bin/CalendarParser.o -c

	ar cr bin/libcparse.a bin/CalendarParser.o

pyth: bin/CalendarParser.o bin/LinkedListAPI.o

	gcc -std=c11 -shared -Iinclude -o bin/icallib.so -fPIC bin/CalendarParser.o bin/LinkedListAPI.o

clean:
	rm bin/LinkedListAPI.o bin/libllist.a bin/CalendarParser.o bin/libcparse.a bin/A2main
	rm -rf *.o *.so
