#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/rwsem.h>
#include <linux/atomic.h>

#define NUM_READERS 5
#define NUM_WRITERS 3
#define NUM_ITERATIONS 20
#define WORK_DELAY_MS 10

/* Thread data */
struct thread_stats {
	int id;
	int iterations_completed;
	atomic_t active;
} __attribute__((__aligned__(64))); /* Prevent false sharing */

static atomic_t shared_counter = ATOMIC_INIT(0);
static struct rw_semaphore rw_sem;

static struct thread_stats reader_stats[NUM_READERS];
static struct thread_stats writer_stats[NUM_WRITERS];
static struct task_struct *readers[NUM_READERS];
static struct task_struct *writers[NUM_WRITERS];

/* Reader thread */
static int reader_thread(void *arg)
{
	int i;
	struct thread_stats *stats = (struct thread_stats *)arg;
	int local_value;

	atomic_set(&stats->active, 1);

	for (i = 0; i < NUM_ITERATIONS; i++) {
		if (kthread_should_stop()) {
			pr_info("Reader %d terminating!\n", stats->id);
			break;
		}

		down_read(&rw_sem);
		local_value = atomic_read(&shared_counter);
		msleep(WORK_DELAY_MS);
		up_read(&rw_sem);

		pr_info("Reader %d: read value = %d, iteration = %d\n",
			stats->id, local_value, i + 1);
		stats->iterations_completed++;
		cond_resched();
	}

	atomic_set(&stats->active, 0);
	return 0;
}

/* Writer thread */
static int writer_thread(void *arg)
{
	int i;
	struct thread_stats *stats = (struct thread_stats *)arg;
	int new_value;

	atomic_set(&stats->active, 1);

	for (i = 0; i < NUM_ITERATIONS; i++) {
		if (kthread_should_stop()) {
			pr_info("Writer %d terminating!\n", stats->id);
			break;
		}

		down_write(&rw_sem);
		new_value = atomic_read(&shared_counter) + 1;
		atomic_set(&shared_counter, new_value);
		msleep(WORK_DELAY_MS);
		up_write(&rw_sem);

		pr_info("Writer %d: wrote value = %d, iteration = %d\n",
			stats->id, new_value, i + 1);
		stats->iterations_completed++;
		cond_resched();
	}

	atomic_set(&stats->active, 0);

	return 0;
}

/* module init */
static int __init rw_init(void)
{
	int i, j;
	pr_info("Reader-Writer kernel module: Initializing\n");

	init_rwsem(&rw_sem);

	/* create readers */
	for (i = 0; i < NUM_READERS; i++) {
		reader_stats[i].id = i + 1;
		reader_stats[i].iterations_completed = 0;
		atomic_set(&reader_stats[i].active, 0);
		readers[i] = kthread_run(reader_thread, &reader_stats[i],
					 "kreader-%d", i + 1);
		if (IS_ERR(readers[i])) {
			pr_err("Failed to create reader %d\n", i + 1);
			for (j = 0; j < i; j++) {
				if (readers[j] && !IS_ERR(readers[j])) {
					kthread_stop(readers[j]);
				}
			}
			return PTR_ERR(readers[i]);
		}
	}

	/* create writers */
	for (i = 0; i < NUM_WRITERS; i++) {
		writer_stats[i].id = i + 1;
		writer_stats[i].iterations_completed = 0;
		atomic_set(&writer_stats[i].active, 0);
		writers[i] = kthread_run(writer_thread, &writer_stats[i],
					 "kwriter-%d", i + 1);
		if (IS_ERR(writers[i])) {
			pr_err("Failed to create writer %d\n", i + 1);
			for (j = 0; j < i; j++) {
				if (writers[j] && !IS_ERR(writers[j])) {
					kthread_stop(writers[j]);
				}
			}
			for (j = 0; j < NUM_READERS; j++) {
				if (readers[j] && !IS_ERR(readers[j])) {
					kthread_stop(readers[j]);
				}
			}
			return PTR_ERR(writers[i]);
		}
	}

	return 0;
}

/* unload module */
static void __exit rw_exit(void)
{
	int i;

	pr_info("Reader-writer module unloaded\n");
	// atomic_set(&module_exiting, 1);
	// msleep(3 * WORK_DELAY_MS);		/* wait for threads to react */

	/* stopping readers */
	for (i = 0; i < NUM_READERS; i++) {
		if (atomic_read(&reader_stats[i].active) &&
		    !IS_ERR_OR_NULL(readers[i])) {
			kthread_stop(readers[i]);
			readers[i] = NULL;
		}
	}

	/* stopping writers*/
	for (i = 0; i < NUM_WRITERS; i++) {
		if (atomic_read(&writer_stats[i].active) &&
		    !IS_ERR_OR_NULL(writers[i])) {
			kthread_stop(writers[i]);
			writers[i] = NULL;
		}
	}

	/* print stats */
	pr_info("\n=== KERNEL STATISTICS ===\n");
	for (i = 0; i < NUM_READERS; i++) {
		pr_info("Reader %d completed %d/%d iterations\n",
			reader_stats[i].id,
			reader_stats[i].iterations_completed, NUM_ITERATIONS);
	}
	for (i = 0; i < NUM_WRITERS; i++) {
		pr_info("Writer %d completed %d/%d iterations\n",
			writer_stats[i].id,
			writer_stats[i].iterations_completed, NUM_ITERATIONS);
	}
	pr_info("Final value of shared_data: %d\n",
		atomic_read(&shared_counter));
}

module_init(rw_init);
module_exit(rw_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Jack");
MODULE_DESCRIPTION("Reader-writer module example");