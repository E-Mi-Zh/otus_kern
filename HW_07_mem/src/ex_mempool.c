#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/mempool.h>
#include <linux/slab.h>
#include <linux/ktime.h>

/* Module parameter for pool element size in KB */
static unsigned int element_size_kb = 1; /* Default: 1KB */
module_param(element_size_kb, uint, 0644);
MODULE_PARM_DESC(element_size_kb,
		 "Pool element size in kilobytes (default: 1)");

/* Module parameter for number of objects in pool */
static unsigned int pool_size = 1; /* Default: 1 */
module_param(pool_size, uint, 0644);
MODULE_PARM_DESC(pool_size, "Number of objects in pool (default: 1)");

static mempool_t *my_mempool;
static void **objects;

static void *mempool_alloc_fn(gfp_t gfp_mask, void *pool_data)
{
	u64 alloc_size_bytes = (u64)element_size_kb * 1024;

	return kmalloc(alloc_size_bytes, gfp_mask);
}

static void mempool_free_fn(void *element, void *pool_data)
{
	kfree(element);
}

static void test_mempool_allocation(void)
{
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i;
	u64 alloc_size_bytes = (u64)element_size_kb * 1024;

	pr_info("mempool: creating pool with %d elements of %llu byte each\n",
		pool_size, alloc_size_bytes);

	/* Create mempool */
	my_mempool = mempool_create(pool_size, mempool_alloc_fn,
				    mempool_free_fn, NULL);
	if (!my_mempool) {
		pr_err("mempool: FAIL, err_msg = Pool creation failed\n");
		return;
	}

	pr_info("mempool: SUCCESS - pool created\n");

	start_time = ktime_get();

	/* Allocate from mempool */
	for (i = 0; i < pool_size; i++) {
		objects[i] = mempool_alloc(my_mempool, GFP_KERNEL);
		if (!objects[i]) {
			pr_err("mempool: FAIL at element %d\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / pool_size;

	pr_info("mempool: %d elements allocated, avg time per element: %lld ns, type: PHYSICALLY_CONTIGUOUS\n",
		pool_size, alloc_time_ns);

cleanup:
	/* Free elements back to pool */
	for (i = 0; i < pool_size; i++) {
		if (objects[i]) {
			mempool_free(objects[i], my_mempool);
		}
	}
}

static int __init mempool_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	objects = kmalloc(pool_size * sizeof(void *), GFP_KERNEL);
	if (!objects) {
		pr_err("[INIT]: fail to alloc objects array!\n");
		return -ENOMEM;
	}

	test_mempool_allocation();

	return 0;
}

static void __exit mempool_module_exit(void)
{
	if (objects != NULL) {
		kfree(objects);
	}
	if (my_mempool) {
		mempool_destroy(my_mempool);
		pr_info("[EXIT] mempool: pool destroyed\n");
	}

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(mempool_module_init);
module_exit(mempool_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Mempool allocation example module");