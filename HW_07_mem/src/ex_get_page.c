#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/gfp.h>
#include <linux/ktime.h>
#include <linux/vmalloc.h>

/* Module parameter for number of pages */
static unsigned long num_pages = 1;
module_param(num_pages, ulong, 0644);
MODULE_PARM_DESC(num_pages, "Number of pages to allocate (default: 1)");

static struct page **pages;

static void test_get_page_allocation(void)
{
	ktime_t start_time, end_time;
	s64 alloc_time_ns;
	unsigned long i;

	pr_info("get_page: allocating %lu pages\n", num_pages);

	start_time = ktime_get();

	for (i = 0; i < num_pages; i++) {
		pages[i] = alloc_page(GFP_KERNEL);
		if (!pages[i]) {
			pr_err("get_page: FAIL at page %lu\n", i);
			goto cleanup;
		}
	}

	end_time = ktime_get();
	alloc_time_ns =
		ktime_to_ns(ktime_sub(end_time, start_time)) / num_pages;

	pr_info("get_page: SUCCESS\n");
	pr_info("get_page: %lu pages allocated, avg time per page: %lld ns, type: PHYSICAL_PAGE\n",
		num_pages, alloc_time_ns);

cleanup:
	for (i = 0; i < num_pages; i++) {
		if (pages[i]) {
			__free_page(pages[i]);
		}
	}
}

static int __init get_page_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	pages = vmalloc(num_pages * sizeof(struct page *));
	if (!pages) {
		pr_err("[INIT]: fail to alloc pages array!\n");
		return -ENOMEM;
	}
	test_get_page_allocation();

	return 0;
}

static void __exit get_page_module_exit(void)
{
	if (pages != NULL) {
		vfree(pages);
	}
	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
}

module_init(get_page_module_init);
module_exit(get_page_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Get_page allocation example module");