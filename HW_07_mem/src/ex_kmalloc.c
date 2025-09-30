#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/ktime.h>

#define NUM_ALLOCS 100

/* Module parameter for allocation size in KB */
static unsigned int alloc_size_kb = 4;  /* Default: 4KB */
module_param(alloc_size_kb, uint, 0644);
MODULE_PARM_DESC(alloc_size_kb, "Allocation size in kilobytes (default: 4)");

static void test_kmalloc_allocation(void)
{
	void *ptr;
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i;

	pr_info("kmalloc: %d byte\n", alloc_size_kb * 1024);

	start_time = ktime_get();

	ptr = kmalloc(alloc_size_kb * 1024, GFP_KERNEL);
	if (!ptr) {
		pr_err("kmalloc: FAIL, err_msg = Allocation failed\n");
		return;
	}
	end_time = ktime_get();
	kfree(ptr);

	pr_info("kmalloc: SUCCESS\n");
	alloc_time_ns = ktime_to_ns(ktime_sub(end_time, start_time));
	pr_info("kmalloc: %d byte, %lld ns, type: PHYSICALLY_CONTIGUOUS\n",
		alloc_size_kb * 1024, alloc_time_ns);

	/* Test multiple allocations */
	start_time = ktime_get();
	for (i = 0; i < NUM_ALLOCS; i++) {
		void *temp_ptr = kmalloc(alloc_size_kb * 1024, GFP_KERNEL);
		if (temp_ptr) {
			kfree(temp_ptr);
		}
	}
	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / NUM_ALLOCS;
	pr_info("kmalloc: multiple alloc/free test. %d operations, avg time: %lld ns\n",
		i, alloc_time_ns);
}

static int __init kmalloc_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	test_kmalloc_allocation();

	return 0;
}

static void __exit kmalloc_module_exit(void)
{
	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(kmalloc_module_init);
module_exit(kmalloc_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Kmalloc allocation example module");