CC      := gcc
CFLAGS  := -O2 -Wall -Wextra -pthread

# Executable names
BIN_NAIVE := sloppy-counter
BIN_OPT   := sloppy-counter-opt
BIN_ATOMIC := atomic-counter
BIN_MUTEX  := mutex-counter
BIN_RACE   := race-counter
# Source files
SRC_NAIVE := sloppy-counter.c
SRC_OPT   := sloppy-counter-opt.c
SRC_ATOMIC := atomic-counter.c
SRC_MUTEX  := mutex-counter.c
SRC_RACE   := race-counter.c	
.PHONY: all clean

all: $(BIN_NAIVE) $(BIN_OPT) $(BIN_ATOMIC) $(BIN_MUTEX) $(BIN_RACE)

$(BIN_NAIVE): $(SRC_NAIVE)
	$(CC) $(CFLAGS) $(SRC_NAIVE) -o $(BIN_NAIVE)

$(BIN_OPT): $(SRC_OPT)
	$(CC) $(CFLAGS) $(SRC_OPT) -o $(BIN_OPT)

$(BIN_ATOMIC): $(SRC_ATOMIC)
	$(CC) $(CFLAGS) $(SRC_ATOMIC) -o $(BIN_ATOMIC)

$(BIN_MUTEX): $(SRC_MUTEX)
	$(CC) $(CFLAGS) $(SRC_MUTEX) -o $(BIN_MUTEX)

$(BIN_RACE): $(SRC_RACE)
	$(CC) $(CFLAGS) $(SRC_RACE) -o $(BIN_RACE)

clean:
	rm -f $(BIN_NAIVE) $(BIN_OPT)
