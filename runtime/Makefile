CC = gcc
PYTHON_CONFIG = python3-config
# Use -O3 with -fno-strict-aliasing to prevent issues with type punning
CFLAGS = -Wall -Wextra -O3 -std=c11 -march=native -mtune=native -fno-strict-aliasing -funroll-loops -finline-functions $(shell $(PYTHON_CONFIG) --cflags --embed 2>/dev/null || $(PYTHON_CONFIG) --cflags)
LDFLAGS = -lm -lgmp $(shell $(PYTHON_CONFIG) --ldflags --embed 2>/dev/null || $(PYTHON_CONFIG) --ldflags)

TARGET = vm
SRC = vm.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
