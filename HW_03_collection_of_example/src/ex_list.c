#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/module.h>
#include <linux/list.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION(
	"Linux kernel module for linked list operations demonstration");

static char *cmd = NULL;
static int value = 0;

struct my_data {
	int data;
	struct list_head list;
};

// list initialisation
static LIST_HEAD(my_list);

// Add item to list
static void add_item(int val)
{
	struct my_data *item = kmalloc(sizeof(struct my_data), GFP_KERNEL);
	if (item == NULL) {
		pr_err("Failed to allocate memory for new item\n");
		return;
	}

	item->data = val;
	INIT_LIST_HEAD(&item->list);
	list_add_tail(&item->list, &my_list);

	pr_info("Added item: %d\n", val);
}

// Find item in list
static void find_item(int val)
{
	struct my_data *item;

	list_for_each_entry(item, &my_list, list) {
		if (item->data == val) {
			pr_info("Item %d found in list\n", val);
			return;
		}
	}

	pr_info("Item %d not found in list\n", val);
}

// Delete item from list
static void del_item(int val)
{
	struct my_data *item;
	struct my_data *tmp;

	list_for_each_entry_safe(item, tmp, &my_list, list) {
		if (item->data == val) {
			list_del(&item->list);
			kfree(item);
			pr_info("Deleted item: %d\n", val);
			return;
		}
	}

	pr_info("Item %d not found in list\n", val);
}

// Print list items
static void print_list(void)
{
	struct my_data *item;

	if (list_empty(&my_list)) {
		pr_info("List is empty\n");
		return;
	}

	pr_info("List contents:");
	list_for_each_entry(item, &my_list, list) {
		pr_cont(" %d", item->data);
	}
	pr_cont("\n");
}

// Reverse list
static void reverse_list(void)
{
	struct list_head *pos, *n;
	struct list_head new_list;

	INIT_LIST_HEAD(&new_list);

	list_for_each_safe(pos, n, &my_list) {
		list_move(pos, &new_list);
	}

	list_replace(&new_list, &my_list);
	pr_info("List reversed\n");
}

// Swap neighbor items
static void swap_neighbors(int val)
{
	struct my_data *item, *next_item;

	list_for_each_entry(item, &my_list, list) {
		if (item->data == val && !list_is_last(&item->list, &my_list)) {
			next_item = list_entry(item->list.next, struct my_data,
					       list);

			int temp = item->data;
			item->data = next_item->data;
			next_item->data = temp;

			pr_info("Swapped items: %d and %d\n", item->data,
				next_item->data);
			return;
		}
	}

	pr_info("Item %d not found or is last in list\n", val);
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, value);

	if (strcmp(cmd, "add") == 0) {
		add_item(value);
	} else if (strcmp(cmd, "del") == 0) {
		del_item(value);
	} else if (strcmp(cmd, "find") == 0) {
		find_item(value);
	} else if (strcmp(cmd, "print") == 0) {
		print_list();
	} else if (strcmp(cmd, "reverse") == 0) {
		reverse_list();
	} else if (strcmp(cmd, "swap") == 0) {
		swap_neighbors(value);
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: add, del, find, print, reverse, swap\n");
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

static int param_set_val(const char *val, const struct kernel_param *kp)
{
	int ret;

	ret = param_set_int(val, kp);
	if (ret != 0)
		return ret;

	pr_info("Param val set to: %d\n", value);

	return 0;
}

static const struct kernel_param_ops cmd_ops = { .set = param_set_cmd,
						 .get = param_get_charp,
						 .free = param_free_charp };

static const struct kernel_param_ops value_ops = {
	.set = param_set_val,
	.get = param_get_int,
};

// Register parameters with callbacks
module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(cmd, "List commands: add, del, find, print, reverse, swap");
module_param_cb(value, &value_ops, &value, 0644);
MODULE_PARM_DESC(value, "Value for list operations");

// Module initialization
static int __init list_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/ex_list/parameters/cmd");
		pr_info("and echo 'value' > /sys/module/ex_list/parameters/value");
		pr_info("to control the list\n");
	}

	return 0;
}

// Module cleanup
static void __exit list_module_exit(void)
{
	struct my_data *item, *tmp;

	pr_info("Cleaning up list...\n");
	list_for_each_entry_safe(item, tmp, &my_list, list) {
		list_del(&item->list);
		kfree(item);
	}

	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(list_module_init);
module_exit(list_module_exit);