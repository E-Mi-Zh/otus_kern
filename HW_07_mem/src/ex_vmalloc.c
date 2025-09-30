#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/vmalloc.h>
#include <linux/ktime.h>

/* Module parameter for allocation size in KB */
static unsigned int alloc_size_kb = 4; /* Default: 4KB */
module_param(alloc_size_kb, uint, 0644);
MODULE_PARM_DESC(alloc_size_kb, "Allocation size in kilobytes (default: 4)");

static void test_vmalloc_allocation(void)
{
	void *ptr;
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	u64 alloc_size_bytes = (u64)alloc_size_kb * 1024;

	pr_info("vmalloc: %d alloc_size_kb\n", alloc_size_kb);
	pr_info("vmalloc: %llu byte\n", alloc_size_bytes);

	start_time = ktime_get();

	ptr = vmalloc(alloc_size_bytes);
	if (!ptr) {
		pr_err("vmalloc: FAIL, err_msg = Allocation failed\n");
		return;
	}
	end_time = ktime_get();
	vfree(ptr);

	pr_info("vmalloc: SUCCESS\n");
	alloc_time_ns = ktime_to_ns(ktime_sub(end_time, start_time));
	pr_info("vmalloc: %llu byte, %lld ns, type: VIRTUAL_NON_CONTIGUOUS\n",
		alloc_size_bytes, alloc_time_ns);
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