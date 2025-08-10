PWD := $(shell pwd)
KDIR ?= /lib/modules/$(shell uname -r)/build
MODULE_NAME := hello_world

SRC_DIR := $(PWD)/src
BUILD_DIR := $(PWD)/build
BUILD_FILES += $(SRC_DIR)/*.ko
EXTRA_CFLAGS := -Wall

CLANG_FORMAT_VERS ?= 19
CLANG_FORMAT := clang-format-$(CLANG_FORMAT_VERS)
CLANG_FORMAT_FLAGS += -i
FORMAT_FILES := $(SRC_DIR)/*.c

CONFIG_MODULE_SIG=n

$(shell mkdir -p $(BUILD_DIR))

all:
	$(MAKE) -C $(KDIR) M=$(PWD) EXTRA_CFLAGS="$(EXTRA_CFLAGS)" modules
	cp $(BUILD_FILES) $(BUILD_DIR)/.

format:
	$(CLANG_FORMAT) $(CLANG_FORMAT_FLAGS) $(FORMAT_FILES)

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

check: install
	modprobe $(MODULE_NAME)
	python3 checker/main.py $(MODULE_NAME)
	rmmod $(MODULE_NAME)

install: all
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

uninstall:
	rm /lib/modules/$(shell uname -r)/extra/src/$(MODULE_NAME).ko

#install: all
#	@echo "Installing module..."
#	sudo install -m 644 -D $(BUILD_DIR)/$(MODULE_NAME).ko /lib/modules/$(shell uname -r)/extra/$(MODULE_NAME).ko
#	sudo depmod -a
#	@echo "Module installed. Run 'sudo modprobe my_module' to load it."

.PHONY: all clean format check
