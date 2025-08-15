#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>
#include <linux/list.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for brackets sequence validation");

static char *input = NULL;
static char *cmd = NULL;

struct bracket_entry {
	char bracket;
	struct list_head list;
};

static LIST_HEAD(stack_top);

static bool is_stack_empty(void)
{
	return list_empty(&stack_top);
}

// Push item
static void stack_push(char bracket)
{
	struct bracket_entry *entry =
		kmalloc(sizeof(struct bracket_entry), GFP_KERNEL);
	if (!entry) {
		pr_err("Failed to allocate memory for stack entry\n");
		return;
	}

	entry->bracket = bracket;
	list_add(&entry->list, &stack_top);
}

// Pop item
static char stack_pop(void)
{
	if (is_stack_empty())
		return '\0';

	struct bracket_entry *entry =
		list_first_entry(&stack_top, struct bracket_entry, list);
	char bracket = entry->bracket;
	list_del(&entry->list);
	kfree(entry);

	return bracket;
}

static void clear_stack(void)
{
	while (!is_stack_empty()) {
		stack_pop();
	}
}

// Check bracket match
static bool is_matching_pair(char opening, char closing)
{
	return (((opening == '(') && (closing == ')')) ||
		((opening == '[') && (closing == ']')) ||
		((opening == '{') && (closing == '}')));
}

// Check brackets sequence for correctness
static void validate_brackets(const char *str)
{
	unsigned int i;
	char c;
	char top;

	clear_stack();
	pr_info("Validating: %s\n", str);

	for (i = 0; str[i] != '\0'; i++) {
		c = str[i];

		// Skip all non bracket chars
		if ((c != '(') && (c != ')') && (c != '[') && (c != ']') &&
		    (c != '{') && (c != '}')) {
			continue;
		}

		if ((c == '(') || (c == '[') || (c == '{')) {
			stack_push(c);
		} else {
			if (is_stack_empty()) {
				pr_info("Result: INVALID (unmatched closing bracket)\n");
				return;
			}

			top = stack_pop();
			if (!is_matching_pair(top, c)) {
				pr_info("Result: INVALID (mismatched brackets %c and %c)\n",
					top, c);
				return;
			}
		}
	}

	if (is_stack_empty()) {
		pr_info("Result: VALID\n");
	} else {
		pr_info("Result: INVALID (unmatched opening brackets)\n");
	}
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	if (strcmp(cmd, "validate") == 0) {
		if (!input) {
			pr_info("No input string provided\n");
			return;
		}
		validate_brackets(input);
	} else if (strcmp(cmd, "clear") == 0) {
		clear_stack();
		pr_info("Stack cleared\n");
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: validate, clear\n");
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

static int param_set_input(const char *val, const struct kernel_param *kp)
{
	int ret;
	char *s = strstrip((char *)val);

	ret = param_set_charp(s, kp);
	if (ret != 0)
		return ret;

	pr_info("Param input set to: %s\n", input);
	return 0;
}

static const struct kernel_param_ops cmd_ops = { .set = param_set_cmd,
						 .get = param_get_charp,
						 .free = param_free_charp };

static const struct kernel_param_ops input_ops = { .set = param_set_input,
						   .get = param_get_charp,
						   .free = param_free_charp };

// Register parameters with callbacks
module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(cmd, "Commands: validate, clear");
module_param_cb(input, &input_ops, &input, 0644);
MODULE_PARM_DESC(input, "Input string for validation");

// Module initialization
static int __init bracket_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/%s/parameters/cmd\n",
			KBUILD_MODNAME);
		pr_info("and echo 'input' > /sys/module/%s/parameters/input\n",
			KBUILD_MODNAME);
		pr_info("to control the brackets check\n");
	}
	return 0;
}

// Module cleanup
static void __exit bracket_module_exit(void)
{
	clear_stack();
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(bracket_module_init);
module_exit(bracket_module_exit);