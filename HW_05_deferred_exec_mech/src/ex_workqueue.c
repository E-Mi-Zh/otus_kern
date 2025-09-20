#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/timer.h>
#include <linux/interrupt.h>
#include <linux/jiffies.h>
#include <linux/atomic.h> /* atomic_t */
#include <linux/workqueue.h> /* workqueue API */

#define TIMER_INTERVAL_MS 1000
#define MAX_WORK_EXECUTIONS 15

static struct timer_list work_timer;
static struct workqueue_struct *my_wq;

static atomic_t timer_count = ATOMIC_INIT(0);
static atomic_t work_count = ATOMIC_INIT(0);

static void my_work_handler(struct work_struct *work);
/* Declare work_struct and register handler */
static DECLARE_WORK(my_work, my_work_handler);

static void my_work_handler(struct work_struct *work)
{
	int tm_count = atomic_read(&timer_count);
	int wrk_count = atomic_inc_return(&work_count);

	pr_info("[WORKQUEUE] Execution %d. Timer triggered %d\n", wrk_count,
		tm_count);
}

static void timer_interrupt_handler(struct timer_list *timer)
{
	int tm_count;

	if (atomic_read(&work_count) >= MAX_WORK_EXECUTIONS) {
		pr_info("[TIMER] Execution limit %d reached, stopping timer!\n",
			MAX_WORK_EXECUTIONS);
		return;
	}

	tm_count = atomic_inc_return(&timer_count);
	pr_info("[TIMER] Trigger %d. Queueing work...\n", tm_count);

	queue_work(my_wq, &my_work);

	mod_timer(&work_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
}

static int __init workqueue_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	/* create own workqueue (single thread) */
	my_wq = alloc_workqueue("my_workqueue", WQ_UNBOUND, 1);
	if (!my_wq) {
		pr_err("[INIT] Failed to create workqueue\n");
		return -ENOMEM;
	}
	pr_info("[INIT] Workqueue initialized\n");

	timer_setup(&work_timer, timer_interrupt_handler, 0);
	mod_timer(&work_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));

	pr_info("[INIT] Timer started, interval %d ms\n", TIMER_INTERVAL_MS);

	return 0;
}

static void __exit workqueue_module_exit(void)
{
	int tm_count, wrk_count;

	del_timer_sync(&work_timer);
	pr_info("[EXIT] Timer stopped\n");

	cancel_work_sync(&my_work);
	destroy_workqueue(my_wq);
	pr_info("[EXIT] Work cancelled, workqueue deleted\n");

	tm_count = atomic_read(&timer_count);
	wrk_count = atomic_read(&work_count);

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
	pr_info("[EXIT] Statistics: Timer=%d, Work=%d\n", tm_count, wrk_count);
}

module_init(workqueue_module_init);
module_exit(workqueue_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Workqueue example module");
