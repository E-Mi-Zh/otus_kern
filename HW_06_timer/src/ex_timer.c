#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/atomic.h>

#define TIMER_INTERVAL_MS 30000 /* 30 seconds = half minute */
#define TOTAL_TIMER_MS 300000 /* 5 minutes = 300 seconds */
#define MAX_TRIGGERS \
	(TOTAL_TIMER_MS / TIMER_INTERVAL_MS) /* total 10 timer triggers */

static struct timer_list hello_timer;
static atomic_t trigger_count = ATOMIC_INIT(0);
static unsigned long start_time_jiffies;

static void my_timer_callback(struct timer_list *t)
{
	int count = atomic_inc_return(&trigger_count);

	/* will print every 30 seconds, so first message will be in 0:30 s = 0 minute */
	/* second message: 1:00 s = 1 minute */
	/* third message: 1:30 s = 1 minute */
	/* ... */
	/* eight message: 9:00 s = 4 minute */
	/* nine message: 9:30 s = 4 minute */
	/* last message: 10:00 s = 5 minute */
	pr_info("min=%d: Hello, timer!\n", (count / 2));

	if (count < MAX_TRIGGERS) {
		mod_timer(&hello_timer,
			  jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));
	} else {
		pr_info("[TIMER] Timer stopped after %d triggers (%d minutes).\n",
			count, (count * TIMER_INTERVAL_MS / (1000 * 60)));
	}
}

static int __init timer_module_init(void)
{
	pr_info("[INIT] %s module loaded\n", KBUILD_MODNAME);

	start_time_jiffies = jiffies;

	timer_setup(&hello_timer, my_timer_callback, 0);
	mod_timer(&hello_timer, jiffies + msecs_to_jiffies(TIMER_INTERVAL_MS));

	pr_info("[INIT] Timer started. Will trigger every %d seconds (%d ms), up to %d minutes.\n",
		TIMER_INTERVAL_MS / 1000, TIMER_INTERVAL_MS,
		(MAX_TRIGGERS * TIMER_INTERVAL_MS / (1000 * 60)));

	return 0;
}

static void __exit timer_module_exit(void)
{
	unsigned long elapsed_jiffies, elapsed_ms;
	int elapsed_seconds, minutes, seconds;

	del_timer_sync(&hello_timer);

	elapsed_jiffies = jiffies - start_time_jiffies;
	elapsed_ms = jiffies_to_msecs(elapsed_jiffies);
	elapsed_seconds = (int)(elapsed_ms / 1000);
	minutes = elapsed_seconds / 60;
	seconds = elapsed_seconds % 60;

	pr_info("[EXIT] %s module unloaded\n", KBUILD_MODNAME);
	pr_info("[EXIT] Total triggers: %d\n", atomic_read(&trigger_count));
	pr_info("[EXIT] Total runtime: %d minutes %d seconds\n", minutes,
		seconds);
}

module_init(timer_module_init);
module_exit(timer_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION(
	"Example timer module: prints 'min=%d: Hello, timer!' every 30 sec for 5 min");
