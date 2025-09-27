#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/ktime.h>

#define CACHE_SIZE 1024
#define NUM_OBJECTS 1024
#define NUM_ALLOCS 100

static struct kmem_cache *my_cache;
static void *objects[NUM_OBJECTS];

static void test_kmem_cache_allocation(void)
{
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i, j;

	pr_info("kmem_cache: creating cache with object size %d byte\n",
		CACHE_SIZE);

	my_cache = kmem_cache_create("my_test_cache", CACHE_SIZE, 0,
				     SLAB_HWCACHE_ALIGN, NULL);
	if (!my_cache) {
		pr_err("kmem_cache: FAIL, err_msg = Cache creation failed\n");
		return;
	}

	pr_info("kmem_cache: SUCCESS - cache created\n");

	start_time = ktime_get();

	/* Allocate multiple objects from the cache */
	for (i = 0; i < NUM_OBJECTS; i++) {
		objects[i] = kmem_cache_alloc(my_cache, GFP_KERNEL);
		if (!objects[i]) {
			pr_err("kmem_cache: FAIL at object %d\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / NUM_OBJECTS;

	pr_info("kmem_cache: %d objects allocated, avg time per object: %lld ns, type: PHYSICALLY_CONTIGUOUS\n",
		NUM_OBJECTS, alloc_time_ns);

cleanup:
	for (i = 0; i < NUM_OBJECTS; i++) {
		if (objects[i]) {
			kmem_cache_free(my_cache, objects[i]);
		}
	}

	/* Test multiple allocations */
	start_time = ktime_get();
	for (j = 0; j < NUM_ALLOCS; j++) {
		for (i = 0; i < NUM_OBJECTS; i++) {
			objects[i] = kmem_cache_alloc(my_cache, GFP_KERNEL);
			if (!objects[i]) {
				pr_err("kmem_cache: FAIL at iteration %d, object %d\n",
				       j, i);
				break;
			}
			kmem_cache_free(my_cache, objects[i]);
		}
	}
	end_time = ktime_get();
	alloc_time_ns = ktime_to_ns(ktime_sub(end_time, start_time)) /
			NUM_ALLOCS / NUM_OBJECTS;
	pr_info("kmem_cache: multiple alloc/free test. %d operations, avg time: %lld ns\n",
		j, alloc_time_ns);
}

static int __init kmem_cache_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	memset(objects, 0, sizeof(objects));
	test_kmem_cache_allocation();

	return 0;
}

static void __exit kmem_cache_module_exit(void)
{
	if (my_cache) {
		kmem_cache_destroy(my_cache);
		pr_info("[EXIT] kmem_cache: cache destroyed\n");
	}

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(kmem_cache_module_init);
module_exit(kmem_cache_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Kmem_cache allocation example module");