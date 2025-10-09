CC = gcc
PYTHON_CONFIG = python3-config
CFLAGS = -Wall -Wextra -Ofast -std=c11 -march=native -flto -ffast-math -funroll-loops -finline-functions -fomit-frame-pointer $(shell $(PYTHON_CONFIG) --cflags --embed 2>/dev/null || $(PYTHON_CONFIG) --cflags)
LDFLAGS = -lm -lgmp -flto $(shell $(PYTHON_CONFIG) --ldflags --embed 2>/dev/null || $(PYTHON_CONFIG) --ldflags)

TARGET = vm
SRC = vm.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
