PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build

LIST_MODULE := ex_list
QUEUE_MODULE := ex_queue
TREE_MODULE := ex_rb_tree
BITMAP_MODULE := ex_bitmap
BIN_SEARCH_MODULE := ex_bin_search
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
	$(TEST_DIR)/list_tester.py \
	$(TEST_DIR)/queue_tester.py \
	$(TEST_DIR)/tree_tester.py \
	$(TEST_DIR)/bitmap_tester.py \
	$(TEST_DIR)/bin_search_tester.py

$(shell mkdir -p $(BUILD_DIR))

.PHONY: all clean format check install uninstall help

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

check: check-list check-queue check-tree check-bitmap check-bin_search

check-list:
	$(TEST_SCRIPT) list $(LIST_MODULE)

check-queue:
	$(TEST_SCRIPT) queue $(QUEUE_MODULE)

check-tree:
	$(TEST_SCRIPT) tree $(TREE_MODULE)

check-bitmap:
	$(TEST_SCRIPT) bitmap $(BITMAP_MODULE)

check-bin_search:
	$(TEST_SCRIPT) bin_search $(BIN_SEARCH_MODULE)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Modules installed."
	@echo "Run 'sudo modprobe $(LIST_MODULE)' to load"
	@echo "Run 'sudo modprobe $(QUEUE_MODULE)' to load"
	@echo "Run 'sudo modprobe $(TREE_MODULE)' to load"
	@echo "Run 'sudo modprobe $(BITMAP_MODULE)' to load"
	@echo "Run 'sudo modprobe $(BIN_SEARCH_MODULE)' to load"

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(LIST_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(QUEUE_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(TREE_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(BITMAP_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(BIN_SEARCH_MODULE).ko
	depmod -a
	@echo "Modules uninstalled"

help:
	@echo "Available targets:"
	@echo "  all              - Build the kernel module (default)"
	@echo "  clean            - Clean build artifacts"
	@echo "  format           - Format source code with clang-format"
	@echo "  check            - Test all modules"
	@echo "  check-list       - Test list module"
	@echo "  check-queue      - Test queue module"
	@echo "  check-tree       - Test queue module"
	@echo "  check-bitmap     - Test bitmap module"
	@echo "  check-bin_search - Test bin_search module"
	@echo "  install          - Install module to system"
	@echo "  uninstall        - Remove module from system"
