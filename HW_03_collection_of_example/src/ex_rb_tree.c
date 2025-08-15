#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/rbtree.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Kernel module for Red-Black Tree operations");

static char *cmd = NULL;
static int value = 0;

struct my_data {
	int data;
	struct rb_node node;
};

// RB-tree initialisation
static struct rb_root my_tree = RB_ROOT;

// Add item to tree
static void tree_insert(int val)
{
	struct my_data *new_item = kmalloc(sizeof(*new_item), GFP_KERNEL);
	if (new_item == NULL) {
		pr_err("Failed to allocate memory for new item\n");
		return;
	}

	struct rb_node **new = &(my_tree.rb_node);
	struct rb_node *parent = NULL;

	new_item->data = val;

	while (*new) {
		// struct my_data *this = rb_entry(*new, struct my_data, node);
		struct my_data *this = container_of(*new, struct my_data, node);
		parent = *new;

		if (val < this->data)
			new = &((*new)->rb_left);
		else if (val > this->data)
			new = &((*new)->rb_right);
		else {
			kfree(new_item);
			pr_info("Insert failed, item %d already exist in tree\n",
				val);
			return;
		}
	}

	rb_link_node(&new_item->node, parent, new);
	rb_insert_color(&new_item->node, &my_tree);
	pr_info("Inserted: %d\n", value);
	return;
}

// Find item in tree
static struct my_data *tree_search(int val)
{
	struct rb_node *node = my_tree.rb_node;

	while (node) {
		struct my_data *item = rb_entry(node, struct my_data, node);

		if (val < item->data)
			node = node->rb_left;
		else if (val > item->data)
			node = node->rb_right;
		else
			return item;
	}
	return NULL;
}

// Del item from tree
static void tree_delete(int val)
{
	struct my_data *item = tree_search(val);
	if (item) {
		rb_erase(&item->node, &my_tree);
		kfree(item);
		pr_info("Deleted: %d\n", value);
	}
}

// Print tree items
static void print_tree(void)
{
	struct rb_node *node;

	if (RB_EMPTY_ROOT(&my_tree)) {
		pr_info("Tree is empty\n");
		return;
	}

	pr_info("RB-Tree contents (in-order):\n");

	for (node = rb_first(&my_tree); node; node = rb_next(node)) {
		struct my_data *item = rb_entry(node, struct my_data, node);
		pr_info("%d (%s)\n", item->data,
			(node->__rb_parent_color & 1) ? "red" : "black");
	}
}

// Clear tree items
static void clear_tree(void)
{
	struct my_data *item;
	struct rb_node *node;

	for (node = rb_first(&my_tree); node; node = rb_first(&my_tree)) {
		item = rb_entry(node, struct my_data, node);
		rb_erase(node, &my_tree);
		kfree(item);
	}

	pr_info("Tree cleared\n");
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, value);

	if (strcmp(cmd, "insert") == 0) {
		tree_insert(value);
	} else if (strcmp(cmd, "delete") == 0) {
		tree_delete(value);
	} else if (strcmp(cmd, "find") == 0) {
		if (tree_search(value))
			pr_info("Found: %d\n", value);
		else
			pr_info("Not found: %d\n", value);
	} else if (strcmp(cmd, "print") == 0) {
		print_tree();
	} else if (strcmp(cmd, "clear") == 0) {
		clear_tree();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: insert, delete, find, print, clear\n");
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
MODULE_PARM_DESC(cmd, "Command: insert, delete, find, print, clear");
module_param_cb(value, &value_ops, &value, 0644);
MODULE_PARM_DESC(value, "Value for tree operations");

static int __init tree_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/ex_rb_tree/parameters/cmd");
		pr_info("and echo 'value' > /sys/module/ex_rb_tree/parameters/value");
		pr_info("to control the tree\n");
	}
	return 0;
}

static void __exit tree_module_exit(void)
{
	clear_tree();
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(tree_module_init);
module_exit(tree_module_exit);