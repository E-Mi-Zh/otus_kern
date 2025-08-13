#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/stat.h>

static unsigned int idx = 0;
static char ch_val = 0;
static char my_str[256] = { 0 };
module_param_string(my_str, my_str, sizeof(my_str),
		    S_IRUSR | S_IRGRP | S_IROTH);
MODULE_PARM_DESC(my_str, "String to display characters (read-only)");

static int param_set_idx(const char *val, const struct kernel_param *kp)
{
	int ret;

	ret = param_set_int(val, kp);
	if (ret < 0)
		return ret;

	pr_info("Параметр idx изменён на: %s\n", val);
	return 0;
}

static int param_get_idx(char *buffer, const struct kernel_param *kp)
{
	unsigned int val;

	val = param_get_int(buffer, kp);
	pr_info("Параметр idx равен: %d\n", val);

	return val;
}

static const struct kernel_param_ops param_ops_idx = {
	.set = param_set_idx,
	.get = param_get_idx,
};

module_param_cb(idx, &param_ops_idx, &idx,
		S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
MODULE_PARM_DESC(idx, "Index of character to modify");

static int param_set_ch_val(const char *val, const struct kernel_param *kp)
{
	int ret;

	ret = param_set_charp(val, kp);
	if (ret < 0) {
		return ret;
	}

	pr_info("Параметр ch_val изменён на: %c\n", val[0]);

	if (((int)val[0] < 32) || ((int)val[0] > 126)) {
		pr_warn("Invalid character: must be printable ASCII (32-126)\n");
		return -EINVAL;
	}

	if (idx >= sizeof(my_str) - 1) {
		pr_warn("Invalid index: must be less than %zu\n",
			sizeof(my_str) - 1);
		return -EINVAL;
	}

	my_str[idx] = val[0];

	return ret;
}

static int param_get_ch_val(char *buffer, const struct kernel_param *kp)
{
	int ret;

	ret = param_get_charp(buffer, kp);
	if (ret < 0)
		return ret;
	pr_info("Параметр ch_val равен: %s\n", buffer);

	return ret;
}

static const struct kernel_param_ops param_ops_ch_val = {
	.set = param_set_ch_val,
	.get = param_get_ch_val,
	.free = param_free_charp
};

module_param_cb(ch_val, &param_ops_ch_val, &ch_val,
		S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
MODULE_PARM_DESC(ch_val, "ASCII code of character (visible) to set");

static int __init hello_init(void)
{
	pr_info("init\n");
	return 0;
}

static void __exit hello_exit(void)
{
	pr_info("exit\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("A simple Hello World module with parameters and callbacks");
