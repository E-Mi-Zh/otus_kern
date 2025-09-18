PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build

RW_MODULE := rw_kern
TEST_DIR := checker
TEST_SCRIPT := $(TEST_DIR)/main.py

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -pthread -pedantic -g -fno-omit-frame-pointer
APP_US = rw_us
SRC = $(SRC_DIR)/rw_us.c

SRC_DIR := $(PWD)/src
BUILD_DIR := $(PWD)/build
BUILD_FILES += $(SRC_DIR)/*.ko

PERF_SCRIPT = perf_test.py

CLANG_FORMAT_VERS ?= 19
CLANG_FORMAT := clang-format-$(CLANG_FORMAT_VERS)
CLANG_FORMAT_FLAGS += -i
FORMAT_FILES := $(SRC_DIR)/*.[ch]
PYTHON_FORMAT_TOOL = black
PYTHON_FORMAT_FILES = \
	$(TEST_DIR)/__init__.py \
	$(TEST_DIR)/base_tester.py \
	$(TEST_DIR)/main.py \
	$(TEST_DIR)/rw_kern_tester.py \
	$(TEST_DIR)/rw_us_tester.py \
	perf_test.py \

$(shell mkdir -p $(BUILD_DIR))

# .PHONY: all clean format check install uninstall help
.PHONY: all clean format

all: make app_us

make:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	cp $(BUILD_FILES) $(BUILD_DIR)/.

app_us: $(SRC)
	$(CC) $(CFLAGS) -o $(APP_US) $(SRC)

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f $(APP_US) *.o

format:
	$(CLANG_FORMAT) $(CLANG_FORMAT_FLAGS) $(FORMAT_FILES)
	@echo "Code formatted with clang-format"

format-python:
	$(PYTHON_FORMAT_TOOL) $(PYTHON_FORMAT_FILES)

check: check-kern check-us

check-kern:
	$(TEST_SCRIPT) rw_kern $(RW_MODULE)

check-us:
	$(TEST_SCRIPT) rw_us $(APP_US)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Modules installed."
	@echo "Run 'sudo modprobe $(RW_MODULE)' to load"

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(RW_MODULE).ko
	depmod -a
	@echo "Modules uninstalled"

install-tools:
	sudo apt update
	sudo apt install -y linux-perf python3-pip python3-matplotlib python3-numpy libc6-dbg
	git clone https://github.com/brendangregg/FlameGraph.git
	export PATH=$$PATH:$$(pwd)/FlameGraph

perf:
	sysctl kernel.perf_event_paranoid=-1
	sh -c 'echo 0 > /proc/sys/kernel/kptr_restrict'
	PATH="$(PATH):$(PWD)/FlameGraph" python3 $(PERF_SCRIPT) $(RW_MODULE) $(APP_US)

help:
	@echo "Available APP_USs:"
	@echo "  all              - Build all (default)"
	@echo "  clean            - Clean build artifacts"
	@echo "  format           - Format source code with clang-format"
	@echo "  format-python    - Format Python source code with black"
	@echo "  make             - Build rw kernel module"
	@echo "  app_us           - Build userspace app"
	@echo "  check            - Test all"
	@echo "  check-kern       - Test rw module"
	@echo "  check-us         - Test userspace app"
	@echo "  load             - Load rw module"
	@echo "  unload           - Unload rw module"
	@echo "  install          - Install module to system"
	@echo "  uninstall        - Remove module from system"
	@echo "  install-tools    - Install perf requirements"
	@echo "  perf             - Run perf tests"
