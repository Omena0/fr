CC = gcc
PYTHON_CONFIG = python3-config

# Use -O3 with -fno-strict-aliasing to prevent issues with type punning
BASE_CFLAGS = -Wall -Wextra -O3 -std=c11 -march=native -mtune=native -fno-strict-aliasing -funroll-loops -finline-functions
BASE_LDFLAGS = -lm -lgmp

ifeq ($(OS),Windows_NT)
	# Windows build: try to enable embedded Python using the active `py -3` installation.
	# We link against the MSVC import library (pythonXY.lib) and rely on the test harness to add the Python base dir to PATH.
	PY_INC = $(shell py -3 -c "import sysconfig; print(sysconfig.get_paths().get('include',''))")
	PY_BASE = $(shell py -3 -c "import sysconfig; print(sysconfig.get_config_var('base') or '')")
	PY_LIBDIR = $(shell py -3 -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')")
	# sysconfig may report pythonXY.dll; for MinGW we need the MSVC import library (.lib).
	# Prefer versioned pythonXY.lib (full API), otherwise fall back to python3.lib.
	PY_LIB = $(shell py -3 -c "import sysconfig,glob,os; libdir=sysconfig.get_config_var('LIBDIR') or ''; ver=glob.glob(os.path.join(libdir,'python[0-9]*.lib')); py3=glob.glob(os.path.join(libdir,'python3.lib')); print(os.path.basename(sorted(ver)[-1]) if ver else (os.path.basename(py3[0]) if py3 else ''))")
	ifeq ($(strip $(PY_INC)),)
		CFLAGS = $(BASE_CFLAGS) -DFR_NO_PYTHON
		LDFLAGS = $(BASE_LDFLAGS) -lws2_32
	else
		CFLAGS = $(BASE_CFLAGS) -I"$(PY_INC)"
		LDFLAGS = $(BASE_LDFLAGS) "$(PY_LIBDIR)/$(PY_LIB)" -lws2_32
	endif
else
	CFLAGS = $(BASE_CFLAGS) $(shell $(PYTHON_CONFIG) --cflags --embed 2>/dev/null || $(PYTHON_CONFIG) --cflags)
	LDFLAGS = $(BASE_LDFLAGS) $(shell $(PYTHON_CONFIG) --ldflags --embed 2>/dev/null || $(PYTHON_CONFIG) --ldflags)
endif

ifeq ($(OS),Windows_NT)
	TARGET = vm.exe
else
	TARGET = vm
endif
SRC = vm.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f vm vm.exe

.PHONY: all clean

