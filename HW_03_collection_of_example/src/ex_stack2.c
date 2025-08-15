#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include <linux/list.h>
#include <linux/string.h>
#include <linux/ctype.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for stack emulation");

static char *cmd = NULL;

struct stack_entry {
	int data;
	struct list_head list;
};

static LIST_HEAD(stack_head);
static unsigned int stack_size = 0;

static bool is_stack_empty(void)
{
	return list_empty(&stack_head);
}

// Push item
static void stack_push(int data)
{
	struct stack_entry *entry =
		kmalloc(sizeof(struct stack_entry), GFP_KERNEL);
	if (entry == NULL) {
		pr_err("Failed to allocate memory for stack entry\n");
		return;
	}

	entry->data = data;
	list_add(&entry->list, &stack_head);
	stack_size++;
	pr_info("Pushed: %d\n", data);
}

// Pop item
static int stack_pop(void)
{
	if (is_stack_empty()) {
		pr_info("Stack underflow\n");
		return -1;
	}

	struct stack_entry *entry =
		list_first_entry(&stack_head, struct stack_entry, list);
	int data = entry->data;
	list_del(&entry->list);
	kfree(entry);
	stack_size--;

	pr_info("Popped: %d\n", data);
	return data;
}

// Peek item
static int stack_top(void)
{
	if (is_stack_empty()) {
		pr_info("Stack is empty\n");
		return -1;
	}

	struct stack_entry *entry =
		list_first_entry(&stack_head, struct stack_entry, list);

	pr_info("Stack top: %d\n", entry->data);
	return entry->data;
}

static void stack_clear(void)
{
	while (!is_stack_empty()) {
		stack_pop();
	}
	pr_info("Stack cleared\n");
}

// Process commands
static void process_command(void)
{
	int value;

	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, value);

	if (sscanf(cmd, "push %d", &value) == 1) {
		stack_push(value);
	} else if (strcmp(cmd, "pop") == 0) {
		stack_pop();
	} else if (strcmp(cmd, "top") == 0) {
		stack_top();
	} else if (strcmp(cmd, "size") == 0) {
		pr_info("Stack size: %u\n", stack_size);
	} else if (strcmp(cmd, "clear") == 0) {
		stack_clear();
	} else if (strcmp(cmd, "exit") == 0) {
		pr_info("Exiting command processing\n");
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: push N, pop, top, size, clear\n");
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

static const struct kernel_param_ops cmd_ops = { .set = param_set_cmd,
						 .get = param_get_charp,
						 .free = param_free_charp };

module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(cmd, "Stack commands: push N, pop, top, size, clear, exit");

// Module initialization
static int __init stack_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/%s/parameters/cmd\n",
			KBUILD_MODNAME);
		pr_info("to control the stack\n");
	}
	return 0;
}

// Module cleanup
static void __exit stack_module_exit(void)
{
	stack_clear();
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(stack_module_init);
module_exit(stack_module_exit);