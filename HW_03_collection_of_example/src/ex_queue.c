#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/kfifo.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Kernel module for FIFO queue operations");

static char *cmd = NULL;
static int value = 0;

#define MAX_QUEUE_SIZE 32

struct my_data {
	int total;
	DECLARE_KFIFO_PTR(fifo, int);
};

static struct my_data my_queue;

// Add item to queue
static void enqueue_item(int val)
{
	if (kfifo_is_full(&my_queue.fifo)) {
		pr_err("Queue max size %d reached! Cannot enqueue %d\n",
		       MAX_QUEUE_SIZE, val);
		return;
	}

	kfifo_in(&my_queue.fifo, &val, 1);
	my_queue.total += val;
	pr_info("Enqueued: %d\n", val);
}

// Delete item from queue
static void dequeue_item(void)
{
	int val;

	if (kfifo_out(&my_queue.fifo, &val, 1)) {
		my_queue.total -= val;
		pr_info("Dequeued: %d\n", val);
	} else {
		pr_info("Queue is empty\n");
	}
}

// Print first queue item
static void peek_item(void)
{
	int val;
	if (kfifo_peek(&my_queue.fifo, &val)) {
		pr_info("Front item: %d\n", val);
	} else {
		pr_info("Queue is empty\n");
	}
}

// Print queue items
static void print_queue(void)
{
	int val;
	unsigned int len;
	unsigned int i;

	if (kfifo_is_empty(&my_queue.fifo)) {
		pr_info("Queue is empty\n");
		return;
	}

	pr_info("Queue contents (front to back):");
	len = kfifo_len(&my_queue.fifo);
	for (i = 0; i < len; i++) {
		if (kfifo_out(&my_queue.fifo, &val, 1)) {
			pr_cont(" %d", val);
		} else {
			pr_info("Error getting out value\n");
		}
		// Return item to the end
		kfifo_in(&my_queue.fifo, &val, 1);
	}
	pr_cont("\n");
}

// Print sum of values
static void print_total(void)
{
	pr_info("Sum of values: %d\n", my_queue.total);
}

// Clear queue
static void clear_queue(void)
{
	kfifo_reset(&my_queue.fifo);
	pr_info("Queue cleared\n");
}

// Process commands
static void process_command(void)
{
	if (!cmd) {
		pr_info("No command specified\n");
		return;
	}

	if (strcmp(cmd, "enqueue") == 0) {
		enqueue_item(value);
	} else if (strcmp(cmd, "dequeue") == 0) {
		dequeue_item();
	} else if (strcmp(cmd, "peek") == 0) {
		peek_item();
	} else if (strcmp(cmd, "print") == 0) {
		print_queue();
	} else if (strcmp(cmd, "total") == 0) {
		print_total();
	} else if (strcmp(cmd, "clear") == 0) {
		clear_queue();
	} else {
		pr_info("Unknown command: %s\n", cmd);
		pr_info("Available commands: enqueue, dequeue, peek, print, total, clear\n");
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
MODULE_PARM_DESC(cmd,
		 "Queue commands: enqueue, dequeue, peek, print, total, clear");
module_param_cb(value, &value_ops, &value, 0644);
MODULE_PARM_DESC(value, "Value for queue operations");

// Module initialization
static int __init queue_module_init(void)
{
	int ret;

	my_queue.total = 0;

	ret = kfifo_alloc(&my_queue.fifo, MAX_QUEUE_SIZE * sizeof(int),
			  GFP_KERNEL);
	if (ret) {
		pr_err("Failed to allocate queue memory\n");
		return ret;
	}

	pr_info("%s module loaded\n", KBUILD_MODNAME);

	if (cmd) {
		process_command();
	} else {
		pr_info("Use echo 'cmd' > /sys/module/ex_queue/parameters/cmd\n");
		pr_info("and echo 'value' > /sys/module/ex_queue/parameters/value\n");
		pr_info("to control the tree\n");
	}

	return 0;
}

// Module cleanup
static void __exit queue_module_exit(void)
{
	kfifo_free(&my_queue.fifo);
	pr_info("%s module unloaded\n", KBUILD_MODNAME);
}

module_init(queue_module_init);
module_exit(queue_module_exit);