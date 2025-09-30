#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/ktime.h>

#define CACHE_SIZE 1024
#define NUM_OBJECTS 1024

/* Module parameter for cache size in KB */
static unsigned int cache_size_kb = 1; /* Default: 1KB */
module_param(cache_size_kb, uint, 0644);
MODULE_PARM_DESC(cache_size_kb, "Cache size in kilobytes (default: 1)");

/* Module parameter for number of objects in cache */
static unsigned int num_objs = 1; /* Default: 1 */
module_param(num_objs, uint, 0644);
MODULE_PARM_DESC(num_objs, "Number of objects in cache (default: 1)");

static struct kmem_cache *my_cache;
static void **objects;

static void test_kmem_cache_allocation(void)
{
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i;
	u64 cache_size_bytes = (u64) cache_size_kb * 1024;
	u64 total_memory;

	pr_info("kmem_cache: creating cache with object size %d byte\n",
		cache_size_kb * 1024);

	my_cache = kmem_cache_create("my_test_cache", cache_size_bytes, 0,
				     SLAB_HWCACHE_ALIGN, NULL);
	if (!my_cache) {
		pr_err("kmem_cache: FAIL, err_msg = Cache creation failed\n");
		return;
	}

	pr_info("kmem_cache: SUCCESS - cache created\n");

	start_time = ktime_get();

	/* Allocate multiple objects from the cache */
	for (i = 0; i < num_objs; i++) {
		objects[i] = kmem_cache_alloc(my_cache, GFP_KERNEL);
		if (!objects[i]) {
			pr_err("kmem_cache: FAIL at object %d\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns = ktime_to_ns(ktime_sub(end_time, start_time)) / num_objs;

	pr_info("kmem_cache: %u objects allocated, avg time per object: %lld ns, type: PHYSICALLY_CONTIGUOUS\n",
		num_objs, alloc_time_ns);
	pr_info("kmem_cache: total memory size: %llu bytes\n",
		(u64)num_objs * cache_size_bytes);

cleanup:
	for (i = 0; i < num_objs; i++) {
		if (objects[i]) {
			kmem_cache_free(my_cache, objects[i]);
		}
	}
}

static int __init kmem_cache_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	objects = kmalloc(num_objs * sizeof(void *), GFP_KERNEL);
	if (!objects) {
		pr_err("[INIT]: fail to alloc objects array!\n");
		return -ENOMEM;
	}
	test_kmem_cache_allocation();

	return 0;
}

static void __exit kmem_cache_module_exit(void)
{
	if (objects != NULL) {
		kfree(objects);
	}
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