all: list parser A2main

list: src/LinkedListAPI.c

	gcc src/LinkedListAPI.c -Iinclude -std=c11 -o bin/LinkedListAPI.o -c

	ar cr bin/libllist.a bin/LinkedListAPI.o

parser: src/CalendarParser.c

	gcc src/CalendarParser.c -Iinclude -std=c11 -o bin/CalendarParser.o -c

	ar cr bin/libcparse.a bin/CalendarParser.o

A2main: src/A2main.c

	gcc src/A2main.c src/CalendarParser.c src/LinkedListAPI.c -Iinclude -std=c11 -o bin/A2main -g

pyth: src/CalendarParser.c

	gcc -std=c11 -shared -Iinclude -o bin/CalendarParser.so -fPIC src/CalendarParser.c

clean:
	rm bin/LinkedListAPI.o bin/libllist.a bin/CalendarParser.o bin/libcparse.a bin/A2main
	rm -rf *.o *.so
