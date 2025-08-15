#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/bsearch.h>
#include <linux/slab.h>
#include <linux/list.h>
#include <linux/random.h>
#include <linux/sort.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for binary search demonstration");

#define NR_VAL 100

static int search_value = 0;
static char *cmd = NULL;

struct my_struct {
	u32 val;
	struct list_head node;
};

static struct my_struct arr[NR_VAL];
static LIST_HEAD(my_list);
static bool is_sorted = false;

// Compare func
static int fn_cmp_arr(const void *a, const void *b)
{
	const struct my_struct *struct_a = a;
	const struct my_struct *struct_b = b;
	return (int)(struct_a->val - struct_b->val);
}

// Change func
static void fn_swap_arr(void *a, void *b, int size)
{
	struct my_struct *struct_a = a;
	struct my_struct *struct_b = b;
	u32 tmp = struct_b->val;

	struct_b->val = struct_a->val;
	struct_a->val = tmp;
}

static void init_arr(void)
{
	int i;

	INIT_LIST_HEAD(&my_list);

	for (i = 0; i < NR_VAL; i++) {
		get_random_bytes(&arr[i].val, sizeof(u32));
		arr[i].val = arr[i].val % NR_VAL;
		INIT_LIST_HEAD(&arr[i].node);
		list_add_tail(&arr[i].node, &my_list);
	}

	is_sorted = false;
	pr_info("Initialized array with %d random elements\n", NR_VAL);
}

static void sort_arr(void)
{
	sort((void *)arr, NR_VAL, sizeof(struct my_struct), fn_cmp_arr,
	     fn_swap_arr);
	is_sorted = true;
	pr_info("Array sorted\n");
}

// Print array
static void print_arr(void)
{
	struct my_struct *entry;
	bool sorted = true;
	u32 prev = 0;
	int i = 0;

	pr_info("Current array (%d elements):", NR_VAL);

	list_for_each_entry(entry, &my_list, node) {
		pr_cont(" %u", entry->val);

		// Check sort on exit
		if (i > 0 && entry->val < prev) {
			sorted = false;
		}
		prev = entry->val;
		i++;
	}
	pr_cont("\n");
	pr_info("Array is %s\n", is_sorted ? "sorted" : "NOT sorted");
	if (is_sorted && !sorted) {
		pr_warn("Warning: array marked as sorted but elements are out of order!\n");
	}
}

// Find item
static bool search_in_arr(u32 val)
{
	struct my_struct target = { .val = val };
	struct my_struct *result;

	if (!is_sorted) {
		pr_info("Array not sorted, cannot perform binary search\n");
		return false;
	}

	result = bsearch(&target, arr, NR_VAL, sizeof(struct my_struct),
			 fn_cmp_arr);

	if (result) {
		pr_info("Value %u found in array\n", val);
		return true;
	}

	pr_info("Value %u not found in array\n", val);
	return false;
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, search_value);

	if (strcmp(cmd, "search") == 0) {
		search_in_arr(search_value);
	} else if (strcmp(cmd, "sort") == 0) {
		sort_arr();
	} else if (strcmp(cmd, "print") == 0) {
		print_arr();
	} else if (strcmp(cmd, "init") == 0) {
		init_arr();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: init, sort, search, print");
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

static int param_set_value(const char *val, const struct kernel_param *kp)
{
	int ret;

	ret = param_set_int(val, kp);
	if (ret != 0)
		return ret;

	pr_info("Param value set to: %d\n", search_value);

	return 0;
}

static const struct kernel_param_ops cmd_ops = { .set = param_set_cmd,
						 .get = param_get_charp,
						 .free = param_free_charp };

static const struct kernel_param_ops value_ops = {
	.set = param_set_value,
	.get = param_get_int,
};

// Register parameters with callbacks
module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(cmd, "Search commands: init, sort, search, print");
module_param_cb(value, &value_ops, &search_value, 0644);
MODULE_PARM_DESC(value, "Value for search operations");

// Module initialization
static int __init bsearch_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	init_arr();

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/%s/parameters/cmd\n",
			KBUILD_MODNAME);
		pr_info("and echo 'value' > /sys/module/%s/parameters/value\n",
			KBUILD_MODNAME);
		pr_info("to control the binary search\n");
	}

	return 0;
}

// Module cleanup
static void __exit bsearch_module_exit(void)
{
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(bsearch_module_init);
module_exit(bsearch_module_exit);