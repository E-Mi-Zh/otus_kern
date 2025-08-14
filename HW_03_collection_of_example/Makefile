PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build

LIST_MODULE := ex_list
QUEUE_MODULE := ex_queue
TEST_SCRIPT := checker/main.py

SRC_DIR := $(PWD)/src
BUILD_DIR := $(PWD)/build
BUILD_FILES += $(SRC_DIR)/*.ko

CLANG_FORMAT_VERS ?= 19
CLANG_FORMAT := clang-format-$(CLANG_FORMAT_VERS)
CLANG_FORMAT_FLAGS += -i
FORMAT_FILES := $(SRC_DIR)/*.[ch]

$(shell mkdir -p $(BUILD_DIR))

.PHONY: all clean format check install uninstall help

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	cp $(BUILD_FILES) $(BUILD_DIR)/.

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm dmesg_failure.log

format:
	$(CLANG_FORMAT) $(CLANG_FORMAT_FLAGS) $(FORMAT_FILES)
	@echo "Code formatted with clang-format"

check: check-list check-queue

check-list:
	$(TEST_SCRIPT) list $(LIST_MODULE)

check-queue:
	$(TEST_SCRIPT) queue $(QUEUE_MODULE)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Modules installed."
	@echo "Run 'sudo modprobe $(LIST_MODULE)' to load"
	@echo "Run 'sudo modprobe $(QUEUE_MODULE)' to load"

uninstall:
	rm /lib/modules/$(shell uname -r)/extra/src/$(LIST_MODULE).ko
	rm /lib/modules/$(shell uname -r)/extra/src/$(QUEUE_MODULE).ko
	depmod -a
	@echo "Modules uninstalled"

help:
	@echo "Available targets:"
	@echo "  all          - Build the kernel module (default)"
	@echo "  clean        - Clean build artifacts"
	@echo "  format       - Format source code with clang-format"
	@echo "  check        - Build and test all modules"
	@echo "  check-list   - Build and test list module"
	@echo "  check-queue  - Build and test queue module"
	@echo "  install      - Install module to system"
	@echo "  uninstall    - Remove module from system"
