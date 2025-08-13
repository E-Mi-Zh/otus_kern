PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build
MODULE_NAME := ex_list

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

format:
	$(CLANG_FORMAT) $(CLANG_FORMAT_FLAGS) $(FORMAT_FILES)
	@echo "Code formatted with clang-format"

check: install
#	sudo dmesg -C
#	chmod +x $(TEST_SCRIPT)
	modprobe $(MODULE_NAME)
	checker/main.py $(MODULE_NAME)
	rmmod $(MODULE_NAME)
#	sudo ./$(TEST_SCRIPT)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Module installed. Run 'sudo modprobe $(MODULE_NAME)' to load"

uninstall:
	rm /lib/modules/$(shell uname -r)/extra/src/$(MODULE_NAME).ko
	depmod -a
	@echo "Module uninstalled"

help:
	@echo "Available targets:"
	@echo "  all       - Build the kernel module (default)"
	@echo "  clean     - Clean build artifacts"
	@echo "  format    - Format source code with clang-format"
	@echo "  check     - Build and run tests"
	@echo "  install   - Install module to system"
	@echo "  uninstall - Remove module from system"
