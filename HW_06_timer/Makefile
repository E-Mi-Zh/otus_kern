PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build

TIMER_MODULE := ex_timer
TEST_DIR := checker
TEST_SCRIPT := $(TEST_DIR)/main.py

SRC_DIR := $(PWD)/src
BUILD_DIR := $(PWD)/build
BUILD_FILES += $(SRC_DIR)/*.ko

CLANG_FORMAT_VERS ?= 19
CLANG_FORMAT := clang-format-$(CLANG_FORMAT_VERS)
CLANG_FORMAT_FLAGS += -i
FORMAT_FILES := $(SRC_DIR)/*.[ch]
PYTHON_FORMAT_TOOL = black
PYTHON_FORMAT_FILES = \
	$(TEST_DIR)/__init__.py \
	$(TEST_DIR)/base_tester.py \
	$(TEST_DIR)/main.py \
	$(TEST_DIR)/timer_tester.py \

$(shell mkdir -p $(BUILD_DIR))

.PHONY: all clean format check install uninstall load unload help

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	cp $(BUILD_FILES) $(BUILD_DIR)/.

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f dmesg_failure.log

format:
	$(CLANG_FORMAT) $(CLANG_FORMAT_FLAGS) $(FORMAT_FILES)
	@echo "Code formatted with clang-format"

format-python:
	   $(PYTHON_FORMAT_TOOL) $(PYTHON_FORMAT_FILES)

load: all
	insmod $(BUILD_DIR)/$(TIMER_MODULE).ko
	@echo "Module $(TIMER_MODULE) loaded"

unload:
	rmmod $(TIMER_MODULE) || true
	@echo "Module $(TIMER_MODULE) unloaded"

check: check-timer

check-timer:
	$(TEST_SCRIPT) timer $(TIMER_MODULE)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Modules installed."
	@echo "Run 'sudo modprobe $(TIMER_MODULE)' to load"

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(TIMER_MODULE).ko
	depmod -a
	@echo "Modules uninstalled"

help:
	@echo "Available targets:"
	@echo "  all              - Build the kernel module (default)"
	@echo "  clean            - Clean build artifacts"
	@echo "  format           - Format source code with clang-format"
	@echo "  format-python    - Format Python source code with black"
	@echo "  check            - Test all modules"
	@echo "  check-timer      - Test timer module"
	@echo "  install          - Install module to system"
	@echo "  uninstall        - Remove module from system"
	@echo "  load             - Build and load module"
	@echo "  unload           - Unload module
