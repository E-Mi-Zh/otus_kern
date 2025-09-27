#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/gfp.h>
#include <linux/ktime.h>

#define NUM_PAGES 256 /* Number of pages to allocate */

static void test_get_page_allocation(void)
{
	struct page *pages[NUM_PAGES];
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	int i, j;

	pr_info("get_page: allocating %d pages\n", NUM_PAGES);

	start_time = ktime_get();

	for (i = 0; i < NUM_PAGES; i++) {
		pages[i] = alloc_page(GFP_KERNEL);
		if (!pages[i]) {
			pr_err("get_page: FAIL at page %d\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / NUM_PAGES;

	pr_info("get_page: SUCCESS\n");
	pr_info("get_page: %d pages allocated, avg time per page: %lld ns, type: PHYSICAL_PAGE\n",
		NUM_PAGES, alloc_time_ns);

cleanup:
	for (i = 0; i < NUM_PAGES; i++) {
		if (pages[i]) {
			__free_page(pages[i]);
		}
	}
}

static int __init get_page_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	test_get_page_allocation();

	return 0;
}

static void __exit get_page_module_exit(void)
{
	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(get_page_module_init);
module_exit(get_page_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Get_page allocation example module");