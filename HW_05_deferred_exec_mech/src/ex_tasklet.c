#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/timer.h>
#include <linux/interrupt.h>
#include <linux/jiffies.h>
#include <linux/atomic.h> /* atomic_t */

#define TIMER_INTERVAL_MS 1000
#define MAX_TASKLET_EXECUTIONS 15

static struct timer_list tasklet_timer;

static atomic_t timer_count = ATOMIC_INIT(0);
static atomic_t tasklet_count = ATOMIC_INIT(0);

static void my_tasklet_handler(struct tasklet_struct *unused);
/* Declare tasklet struct and register tasklet handler */
static DECLARE_TASKLET(my_tasklet, my_tasklet_handler);

static void my_tasklet_handler(struct tasklet_struct *unused)
{
	int tm_count = atomic_read(&timer_count);
	int tskl_count = atomic_inc_return(&tasklet_count);

	pr_info("[TASKLET] Execution %d. Timer triggered %d\n", tskl_count,
		tm_count);
}

static void timer_interrupt_handler(struct timer_list *timer)
{
	int tm_count;

	if (atomic_read(&tasklet_count) >= MAX_TASKLET_EXECUTIONS) {
		pr_info("[TIMER] Execution limit %d reached, stopping timer!\n",
			MAX_TASKLET_EXECUTIONS);
		return;
	}

	tm_count = atomic_inc_return(&timer_count);

	pr_info("[TIMER] Trigger %d. Scheduling tasklet...\n", tm_count);

	tasklet_schedule(&my_tasklet);

	mod_timer(&tasklet_timer,
		  jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
}

static int __init tasklet_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	timer_setup(&tasklet_timer, timer_interrupt_handler, 0);
	mod_timer(&tasklet_timer,
		  jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));

	pr_info("[INIT] Timer start, interval %d ms.\n", TIMER_INTERVAL_MS);

	return 0;
}

static void __exit tasklet_module_exit(void)
{
	int tm_count, tskl_count;

	del_timer_sync(&tasklet_timer);
	pr_info("[EXIT] Timer stopped\n");

	tasklet_kill(&my_tasklet);

	tm_count = atomic_read(&timer_count);
	tskl_count = atomic_read(&tasklet_count);

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
	pr_info("[EXIT] Statistics: Timer=%d, Tasklet=%d\n", tm_count,
		tskl_count);
}

module_init(tasklet_module_init);
module_exit(tasklet_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Tasklet example module");