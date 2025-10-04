CC = gcc
CFLAGS = -Wall -Wextra -O3 -std=c11 -march=native -flto -ffast-math -funroll-loops -finline-functions -fomit-frame-pointer
LDFLAGS = -lm -lgmp -flto

TARGET = vm
SRC = vm.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

# Profile-Guided Optimization (PGO) - 10-20% speedup
pgo-generate:
	$(CC) $(CFLAGS) -fprofile-generate -o $(TARGET) $(SRC) $(LDFLAGS)

pgo-train: pgo-generate
	@echo "Training with fibonacci benchmark..."
	./$(TARGET) ../src/out.bc
	@echo "Training complete!"

pgo-use:
	$(CC) $(CFLAGS) -fprofile-use -fprofile-correction -o $(TARGET) $(SRC) $(LDFLAGS)
	rm -f *.gcda

pgo: pgo-train pgo-use
	@echo "PGO optimization complete! Binary optimized for fibonacci workload."

clean:
	rm -f $(TARGET) *.gcda

.PHONY: all clean pgo-generate pgo-train pgo-use pgo
