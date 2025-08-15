#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Linux kernel module for binary search tree operations");

static char *cmd = NULL;
static int value = 0;

struct Node {
	int data;
	struct Node *left;
	struct Node *right;
};

static struct Node *root = NULL;

// Create binary tree node
static struct Node *create_node(int data)
{
	struct Node *node = kmalloc(sizeof(struct Node), GFP_KERNEL);
	if (!node) {
		pr_err("Failed to allocate memory for new node\n");
		return NULL;
	}
	node->data = data;
	node->left = node->right = NULL;
	return node;
}

// Insert node to binary search tree
static struct Node *insert_node(struct Node *root, int data)
{
	if (root == NULL) {
		struct Node *new_node = create_node(data);
		if (new_node != NULL)
			pr_info("Inserted node: %d\n", data);
		return new_node;
	}

	if (data < root->data) {
		root->left = insert_node(root->left, data);
	} else if (data > root->data) {
		root->right = insert_node(root->right, data);
	}
	return root;
}

// Find minimum tree node
static struct Node *find_min(struct Node *root)
{
	while ((root != NULL) && (root->left != NULL))
		root = root->left;
	return root;
}

// Delete node from tree
static struct Node *delete_node(struct Node *root, int data)
{
	if (root == NULL) {
		pr_info("Node %d not found for deletion\n", data);
		return root;
	}

	if (data < root->data) {
		root->left = delete_node(root->left, data);
	} else if (data > root->data) {
		root->right = delete_node(root->right, data);
	} else {
		// We have node with one or zero leafs
		if (root->left == NULL) {
			struct Node *temp = root->right;
			kfree(root);
			return temp;
		} else if (root->right == NULL) {
			struct Node *temp = root->left;
			kfree(root);
			return temp;
		}

		// We have node with two leafs
		struct Node *temp = find_min(root->right);
		root->data = temp->data;
		root->right = delete_node(root->right, temp->data);

		pr_info("Deleted node: %d\n", data);
	}
	return root;
}

static void in_order(struct Node *root)
{
	if (root != NULL) {
		in_order(root->left);
		pr_cont(" %d", root->data);
		in_order(root->right);
	}
}

static void print_tree(void)
{
	pr_info("Tree in-order traversal:");
	in_order(root);
	pr_cont("\n");
}

static void free_tree(struct Node *root)
{
	if (root) {
		free_tree(root->left);
		free_tree(root->right);
		kfree(root);
	}
}

static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	pr_info("Executing command: %s %d\n", cmd, value);

	if (strcmp(cmd, "insert") == 0) {
		root = insert_node(root, value);
	} else if (strcmp(cmd, "delete") == 0) {
		root = delete_node(root, value);
	} else if (strcmp(cmd, "print") == 0) {
		print_tree();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: insert, delete, print\n");
	}
}

/* Callbacks и параметры модуля остаются без изменений */
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

module_param_cb(cmd, &cmd_ops, &cmd, 0644);
MODULE_PARM_DESC(cmd, "Tree commands: insert, delete, print");
module_param_cb(value, &value_ops, &value, 0644);
MODULE_PARM_DESC(value, "Value for tree operations");

static int __init tree_module_init(void)
{
	pr_info("%s module loaded\n", KBUILD_MODNAME);

	// Инициализация дерева
	int init_values[] = { 50, 30, 20, 40, 70, 60, 80 };
	for (int i = 0; i < ARRAY_SIZE(init_values); i++) {
		root = insert_node(root, init_values[i]);
	}

	if (cmd)
		process_command();

	return 0;
}

static void __exit tree_module_exit(void)
{
	free_tree(root);
	root = NULL;
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(tree_module_init);
module_exit(tree_module_exit);