#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include <linux/list.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for stack implementation");

static char *cmd = NULL;
static int value = 0;

struct stack_entry {
	int data;
	struct list_head list;
};

static LIST_HEAD(stack_top);

static bool is_stack_empty(void)
{
	return list_empty(&stack_top);
}

// Add item to stack (push)
static void stack_push(int data)
{
	struct stack_entry *entry =
		kmalloc(sizeof(struct stack_entry), GFP_KERNEL);
	if (entry == NULL) {
		pr_err("Failed to allocate memory for stack entry\n");
		return;
	}

	entry->data = data;
	list_add(&entry->list, &stack_top);
	pr_info("Pushed: %d\n", data);
}

// Get item from stack (pop)
static int stack_pop(void)
{
	int data;

	if (is_stack_empty()) {
		pr_info("Stack underflow\n");
		return -1;
	}

	struct stack_entry *entry =
		list_first_entry(&stack_top, struct stack_entry, list);
	data = entry->data;
	list_del(&entry->list);
	kfree(entry);

	pr_info("Popped: %d\n", data);
	return data;
}

// Print stack
static void print_stack(void)
{
	struct stack_entry *entry;

	if (is_stack_empty()) {
		pr_info("Stack is empty\n");
		return;
	}

	pr_info("Stack contents (top to bottom):");
	list_for_each_entry(entry, &stack_top, list) {
		pr_cont(" %d", entry->data);
	}
	pr_cont("\n");
}

static void clear_stack(void)
{
	while (!is_stack_empty()) {
		stack_pop();
	}
	pr_info("Stack cleared\n");
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, value);

	if (strcmp(cmd, "push") == 0) {
		stack_push(value);
	} else if (strcmp(cmd, "pop") == 0) {
		stack_pop();
	} else if (strcmp(cmd, "print") == 0) {
		print_stack();
	} else if (strcmp(cmd, "clear") == 0) {
		clear_stack();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: push, pop, print, clear\n");
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
	int ret = param_set_int(val, kp);
	if (ret == 0)
		pr_info("Param value set to: %d\n", value);
	return ret;
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
MODULE_PARM_DESC(cmd, "Stack commands: push, pop, print, clear");
module_param_cb(value, &value_ops, &value, 0644);
MODULE_PARM_DESC(value, "Value for stack operations");

// Module initialization
static int __init stack_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/%s/parameters/cmd\n",
			KBUILD_MODNAME);
		pr_info("and echo 'value' > /sys/module/%s/parameters/value\n",
			KBUILD_MODNAME);
		pr_info("to control the stack\n");
	}
	return 0;
}

static void __exit stack_module_exit(void)
{
	clear_stack();
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(stack_module_init);
module_exit(stack_module_exit);