#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/bitmap.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for bitmap operations demonstration");

#define MAX_BITS 64

static char *cmd = NULL;
static unsigned int index = 0;

static unsigned long my_bitmap[BITS_TO_LONGS(MAX_BITS)] = { 0 };

// Set bit at pos idx
static void my_set_bit(unsigned int idx)
{
	if (idx >= MAX_BITS) {
		pr_err("Index %u out of bounds (max %d)\n", idx, MAX_BITS - 1);
		return;
	}

	bitmap_set(my_bitmap, idx, 1);
	pr_info("Bit %u set\n", idx);
}

// Clear bit at pos idx
static void my_clear_bit(unsigned int idx)
{
	if (idx >= MAX_BITS) {
		pr_err("Index %u out of bounds (max %d)\n", idx, MAX_BITS - 1);
		return;
	}

	bitmap_clear(my_bitmap, idx, 1);
	pr_info("Bit %u cleared\n", idx);
}

// Check if bit is set
static void my_test_bit(unsigned int idx)
{
	if (idx >= MAX_BITS) {
		pr_err("Index %u out of bounds (max %d)\n", idx, MAX_BITS - 1);
		return;
	}

	if (test_bit(idx, my_bitmap)) {
		pr_info("Bit %u is set\n", idx);
	} else {
		pr_info("Bit %u is not set\n", idx);
	}
}

// Invert bit at pos idx
static void flip_bit(unsigned int idx)
{
	if (idx >= MAX_BITS) {
		pr_err("Index %u out of bounds (max %d)\n", idx, MAX_BITS - 1);
		return;
	}

	change_bit(idx, my_bitmap);
	pr_info("Bit %u flipped\n", idx);
}

// Find first non-zero bit
static void my_find_first_bit(void)
{
	unsigned int idx;

	idx = find_first_bit(my_bitmap, MAX_BITS);
	if (idx < MAX_BITS) {
		pr_info("First set bit found at position %u\n", idx);
	} else {
		pr_info("No set bits found\n");
	}
}

// Find first zero bit
static void find_first_zero(void)
{
	unsigned int idx;

	idx = find_first_zero_bit(my_bitmap, MAX_BITS);
	if (idx < MAX_BITS) {
		pr_info("First zero bit found at position %u\n", idx);
	} else {
		pr_info("All bits are set\n");
	}
}

// Count non-zero bits
static void count_bits(void)
{
	unsigned int count;

	count = bitmap_weight(my_bitmap, MAX_BITS);
	pr_info("Number of set bits: %u\n", count);
}

// Check that all bits are set
static void test_all_bits(void)
{
	if (bitmap_full(my_bitmap, MAX_BITS)) {
		pr_info("All bits are set\n");
	} else {
		pr_info("Not all bits are set\n");
	}
}

// Check that all bits are zeros
static void test_all_zeros(void)
{
	if (bitmap_empty(my_bitmap, MAX_BITS)) {
		pr_info("All bits are clear\n");
	} else {
		pr_info("Not all bits are clear\n");
	}
}

// Print bitmap
static void print_bitmap(void)
{
	char buf[MAX_BITS + 1] = { 0 };
	unsigned int i;

	for (i = 0; i < MAX_BITS; i++) {
		buf[i] = test_bit(i, my_bitmap) ? '1' : '0';
	}
	buf[MAX_BITS] = '\0';

	pr_info("Current bitmap: %s\n", buf);
}

// Clear (zeroing) bitmap
static void clear_bitmap(void)
{
	bitmap_zero(my_bitmap, MAX_BITS);
	pr_info("All bits cleared\n");
}

// Set all bits to 1
static void set_bitmap(void)
{
	bitmap_fill(my_bitmap, MAX_BITS);
	pr_info("All bits set\n");
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %u\n", cmd, index);

	if (strcmp(cmd, "set") == 0) {
		my_set_bit(index);
	} else if (strcmp(cmd, "clear") == 0) {
		my_clear_bit(index);
	} else if (strcmp(cmd, "test") == 0) {
		my_test_bit(index);
	} else if (strcmp(cmd, "flip") == 0) {
		flip_bit(index);
	} else if (strcmp(cmd, "find_set") == 0) {
		my_find_first_bit();
	} else if (strcmp(cmd, "find_zero") == 0) {
		find_first_zero();
	} else if (strcmp(cmd, "count") == 0) {
		count_bits();
	} else if (strcmp(cmd, "test_all_set") == 0) {
		test_all_bits();
	} else if (strcmp(cmd, "test_all_clear") == 0) {
		test_all_zeros();
	} else if (strcmp(cmd, "print") == 0) {
		print_bitmap();
	} else if (strcmp(cmd, "clear_all") == 0) {
		clear_bitmap();
	} else if (strcmp(cmd, "set_all") == 0) {
		set_bitmap();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: set, clear, test, flip, find_set, find_zero,\n");
		pr_info("count, test_all_set, test_all_clear, print, clear_all, set_all\n");
	}
}

static int param_set_cmd(const char *val, const struct kernel_param *kp)
{
	int ret;
	char *s = strstrip((char *)val);

	ret = param_set_charp(s, kp);
	if (ret != 0)
		return ret;

	pr_info("Param cmd set to: %s\n", cmd);

	process_command();

	return 0;
}

static int param_set_index(const char *val, const struct kernel_param *kp)
{
	int ret;

	ret = param_set_uint(val, kp);
	if (ret != 0)
		return ret;

	pr_info("Param index set to: %u\n", index);

	return 0;
}

static const struct kernel_param_ops cmd_ops = { .set = param_set_cmd,
						 .get = param_get_charp,
						 .free = param_free_charp };

static const struct kernel_param_ops index_ops = {
	.set = param_set_index,
	.get = param_get_uint,
};

// Register parameters with callbacks
module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(
	cmd,
	"Bitmap commands: set, clear, test, flip, find_set, find_zero, count, test_all_set, test_all_clear, print, clear_all, set_all");
module_param_cb(index, &index_ops, &index, 0644);
MODULE_PARM_DESC(index, "Bit index for operations (0-63)");

// Module initialization
static int __init bitmap_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/%s/parameters/cmd\n",
			KBUILD_MODNAME);
		pr_info("and echo 'index' > /sys/module/%s/parameters/index\n",
			KBUILD_MODNAME);
		pr_info("to control the bitmap\n");
	}

	return 0;
}

// Module cleanup
static void __exit bitmap_module_exit(void)
{
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(bitmap_module_init);
module_exit(bitmap_module_exit);