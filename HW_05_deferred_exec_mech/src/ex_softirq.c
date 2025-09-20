#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/timer.h>
#include <linux/interrupt.h>
#include <linux/jiffies.h>
#include <linux/atomic.h> /* atomic_t */
#include <linux/rcupdate.h> /* synchronize_rcu() */

#define TIMER_INTERVAL_MS 1000
#define MAX_SOFTIRQ_EXECUTIONS 15

static struct timer_list softirq_timer;

static atomic_t timer_count = ATOMIC_INIT(0);
static atomic_t softirq_count = ATOMIC_INIT(0);

static void my_softirq_handler(struct softirq_action *action)
{
	int tm_count = atomic_read(&timer_count);
	int sirq_count = atomic_inc_return(&softirq_count);

	pr_info("[SOFTIRQ] Execution %d. Timer triggered %d\n", sirq_count,
		tm_count);
}

static void timer_interrupt_handler(struct timer_list *timer)
{
	int tm_count;

	if (atomic_read(&softirq_count) >= MAX_SOFTIRQ_EXECUTIONS) {
		pr_info("[TIMER] Execution limit %d reached, stopping timer!\n",
			MAX_SOFTIRQ_EXECUTIONS);
		return;
	}

	tm_count = atomic_inc_return(&timer_count);

	pr_info("[TIMER] Trigger %d. Raising softirq...\n", tm_count);

	raise_softirq(MY_TIMER_SOFTIRQ);

	mod_timer(&softirq_timer,
		  jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
}

static int __init softirq_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	/* register softirq handler */
	open_softirq(MY_TIMER_SOFTIRQ, my_softirq_handler);
	pr_info("[INIT] Register softirq handler for MY_TIMER_SOFTIRQ\n");

	timer_setup(&softirq_timer, timer_interrupt_handler, 0);
	mod_timer(&softirq_timer,
		  jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));

	pr_info("[INIT] Timer start, interval %d ms.\n", TIMER_INTERVAL_MS);

	return 0;
}

static void __exit softirq_module_exit(void)
{
	int tm_count, sirq_count;

	del_timer_sync(&softirq_timer);
	pr_info("[EXIT] Timer stopped.\n");

	synchronize_rcu();

	tm_count = atomic_read(&timer_count);
	sirq_count = atomic_read(&softirq_count);

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
	pr_info("[EXIT] Statistics: Timer=%d, Softirq=%d\n", tm_count,
		sirq_count);
}

module_init(softirq_module_init);
module_exit(softirq_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Softirq example module");
