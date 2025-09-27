#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/mempool.h>
#include <linux/slab.h>
#include <linux/ktime.h>

#define POOL_SIZE 1024
#define ELEMENT_SIZE 1024
#define NUM_ALLOCS 100

static mempool_t *my_mempool;
static void *test_elements[POOL_SIZE];

static void *mempool_alloc_fn(gfp_t gfp_mask, void *pool_data)
{
	return kmalloc(ELEMENT_SIZE, gfp_mask);
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

	pr_info("mempool: creating pool with %d elements of %d byte each\n",
		POOL_SIZE, ELEMENT_SIZE);

	/* Create mempool */
	my_mempool = mempool_create(POOL_SIZE, mempool_alloc_fn,
				    mempool_free_fn, NULL);
	if (!my_mempool) {
		pr_err("mempool: FAIL, err_msg = Pool creation failed\n");
		return;
	}

	pr_info("mempool: SUCCESS - pool created\n");

	start_time = ktime_get();

	/* Allocate from mempool */
	for (i = 0; i < POOL_SIZE; i++) {
		test_elements[i] = mempool_alloc(my_mempool, GFP_KERNEL);
		if (!test_elements[i]) {
			pr_err("mempool: FAIL at element %d\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / POOL_SIZE;

	pr_info("mempool: %d elements allocated, avg time per element: %lld ns, type: PHYSICALLY_CONTIGUOUS\n",
		POOL_SIZE, alloc_time_ns);

cleanup:
	/* Free elements back to pool */
	for (i = 0; i < POOL_SIZE; i++) {
		if (test_elements[i]) {
			mempool_free(test_elements[i], my_mempool);
		}
	}
}

static int __init mempool_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	test_mempool_allocation();

	return 0;
}

static void __exit mempool_module_exit(void)
{
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