#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/vmalloc.h>
#include <linux/ktime.h>

#define ALLOC_SIZE (1024 * 1024)
#define NUM_ALLOCS 100

static void test_vmalloc_allocation(void)
{
	void *ptr;
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i;

	pr_info("vmalloc: %d byte\n", ALLOC_SIZE);

	start_time = ktime_get();

	ptr = vmalloc(ALLOC_SIZE);
	if (!ptr) {
		pr_err("vmalloc: FAIL, err_msg = Allocation failed\n");
		return;
	}
	end_time = ktime_get();
	vfree(ptr);

	pr_info("vmalloc: SUCCESS\n");
	alloc_time_ns = ktime_to_ns(ktime_sub(end_time, start_time));
	pr_info("vmalloc: %d byte, %lld ns, type: VIRTUAL_NON_CONTIGUOUS\n",
		ALLOC_SIZE, alloc_time_ns);

	/* Test multiple allocations */
	start_time = ktime_get();
	for (i = 0; i < NUM_ALLOCS; i++) {
		void *temp_ptr = vmalloc(ALLOC_SIZE);
		if (temp_ptr) {
			vfree(temp_ptr);
		}
	}
	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / NUM_ALLOCS;
	pr_info("vmalloc: multiple alloc/free test. %d operations, avg time: %lld ns\n",
		i, alloc_time_ns);
}

static int __init vmalloc_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	test_vmalloc_allocation();

	return 0;
}

static void __exit vmalloc_module_exit(void)
{
	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(vmalloc_module_init);
module_exit(vmalloc_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Vmalloc allocation example module");