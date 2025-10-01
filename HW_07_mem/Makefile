PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build

KMALLOC_MODULE := ex_kmalloc
VMALLOC_MODULE := ex_vmalloc
KMEM_CACHE_MODULE := ex_kmem_cache
MEMPOOL_MODULE := ex_mempool
GET_PAGE_MODULE := ex_get_page
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
	$(TEST_DIR)/kmalloc_tester.py \
	$(TEST_DIR)/vmalloc_tester.py \
	$(TEST_DIR)/kmem_cache_tester.py \
	$(TEST_DIR)/mempool_tester.py \

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

check: check-kmalloc check-vmalloc check-kmem_cache check-mempool

check-kmalloc:
	$(TEST_SCRIPT) kmalloc $(KMALLOC_MODULE)

check-vmalloc:
	$(TEST_SCRIPT) vmalloc $(VMALLOC_MODULE)

check-kmem_cache:
	$(TEST_SCRIPT) kmem_cache $(KMEM_CACHE_MODULE)

check-mempool:
	$(TEST_SCRIPT) mempool $(MEMPOOL_MODULE)

install: all
	@echo "Installing module to /lib/modules/$(shell uname -r)/extra/src"
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a
	@echo "Modules installed."
	@echo "Run 'sudo modprobe $(KMALLOC_MODULE)' to load"
	@echo "Run 'sudo modprobe $(VMALLOC_MODULE)' to load"
	@echo "Run 'sudo modprobe $(KMEM_CACHE_MODULE)' to load"
	@echo "Run 'sudo modprobe $(MEMPOOL_MODULE)' to load"
	@echo "Run 'sudo modprobe $(GET_PAGE_MODULE)' to load"

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(KMALLOC_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(VMALLOC_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(KMEM_CACHE_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(MEMPOOL_MODULE).ko
	rm -f /lib/modules/$(shell uname -r)/extra/src/$(GET_PAGE_MODULE).ko

	depmod -a
	@echo "Modules uninstalled"

load-kmalloc: $(BUILD_DIR)/$(KMALLOC_MODULE).ko
	insmod $(BUILD_DIR)/$(KMALLOC_MODULE).ko
	@echo "Module $(KMALLOC_MODULE) loaded"

unload-kmalloc:
	rmmod $(KMALLOC_MODULE) || true
	@echo "Module $(KMALLOC_MODULE) unloaded"

load-vmalloc: $(BUILD_DIR)/$(VMALLOC_MODULE).ko
	insmod $(BUILD_DIR)/$(VMALLOC_MODULE).ko
	@echo "Module $(VMALLOC_MODULE) loaded"

unload-vmalloc:
	rmmod $(VMALLOC_MODULE) || true
	@echo "Module $(VMALLOC_MODULE) unloaded"

load-kmem_cache: $(BUILD_DIR)/$(KMEM_CACHE_MODULE).ko
	insmod $(BUILD_DIR)/$(KMEM_CACHE_MODULE).ko
	@echo "Module $(KMEM_CACHE_MODULE) loaded"

unload-kmem-cache:
	rmmod $(KMEM_CACHE_MODULE) || true
	@echo "Module $(KMEM_CACHE_MODULE) unloaded"

load-mempool: $(BUILD_DIR)/$(MEMPOOL_MODULE).ko
	insmod $(BUILD_DIR)/$(MEMPOOL_MODULE).ko
	@echo "Module $(MEMPOOL_MODULE) loaded"

unload-mempool:
	rmmod $(MEMPOOL_MODULE) || true
	@echo "Module $(MEMPOOL_MODULE) unloaded"

load-get_page: $(BUILD_DIR)/$(GET_PAGE_MODULE).ko
	insmod $(BUILD_DIR)/$(GET_PAGE_MODULE).ko
	@echo "Module $(GET_PAGE_MODULE) loaded"

unload-get_page:
	rmmod $(GET_PAGE_MODULE) || true
	@echo "Module $(GET_PAGE_MODULE) unloaded"

help:
	@echo "Available targets:"
	@echo "  all              - Build the kernel module (default)"
	@echo "  clean            - Clean build artifacts"
	@echo "  format           - Format source code with clang-format"
	@echo "  format-python    - Format Python source code with black"
	@echo "  check            - Test all modules"
	@echo "  check-kmalloc    - Test kmalloc module"
	@echo "  check-vmalloc    - Test vmalloc module"
	@echo "  check-kmem_cache - Test kmem_cache module"
	@echo "  check-mempool - Test mempool module"
	@echo "  install          - Install module to system"
	@echo "  uninstall        - Remove module from system"
