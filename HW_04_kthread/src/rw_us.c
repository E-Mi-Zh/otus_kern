#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdatomic.h>

#define NUM_READERS 5
#define NUM_WRITERS 3
#define NUM_ITERATIONS 20
#define WORK_DELAY_MS 10

/* Thread data */
struct thread_stats {
	int id;
	int iterations_completed;
} __attribute__((__aligned__(64))); /* Prevent false sharing */

atomic_int shared_counter = 0;
pthread_rwlock_t rw_lock = PTHREAD_RWLOCK_INITIALIZER;

struct thread_stats reader_stats[NUM_READERS];
struct thread_stats writer_stats[NUM_WRITERS];
pthread_t readers[NUM_READERS];
pthread_t writers[NUM_WRITERS];

void msleep(int ms)
{
	usleep(ms * 1000);
}

/* Reader thread */
void *reader_thread(void *arg)
{
	int i;
	struct thread_stats *stats = (struct thread_stats *)arg;
	int local_value;

	for (i = 0; i < NUM_ITERATIONS; i++) {
		pthread_rwlock_rdlock(&rw_lock);
		local_value = atomic_load(&shared_counter);
		msleep(WORK_DELAY_MS);
		pthread_rwlock_unlock(&rw_lock);

		printf("Reader %d: read value = %d, iteration = %d\n",
		       stats->id, local_value, i + 1);
		stats->iterations_completed++;
	}
	return NULL;
}

/* Writer thread */
void *writer_thread(void *arg)
{
	int i;
	struct thread_stats *stats = (struct thread_stats *)arg;
	int new_value;

	for (i = 0; i < NUM_ITERATIONS; i++) {
		pthread_rwlock_wrlock(&rw_lock);
		new_value = atomic_load(&shared_counter) + 1;
		atomic_store(&shared_counter, new_value);
		msleep(WORK_DELAY_MS);
		pthread_rwlock_unlock(&rw_lock);

		printf("Writer %d: wrote value = %d, iteration = %d\n",
		       stats->id, new_value, i + 1);
		stats->iterations_completed++;
	}
	return NULL;
}

int main(void)
{
	int i;
	int ret;

	printf("Reader-Writer userspace program: Initializing\n");

	/* create readers */
	for (i = 0; i < NUM_READERS; i++) {
		reader_stats[i].id = i + 1;
		reader_stats[i].iterations_completed = 0;
		ret = pthread_create(&readers[i], NULL, reader_thread,
				     &reader_stats[i]);
		if (ret != 0) {
			fprintf(stderr, "Failed to create reader %d: %d\n",
				i + 1, ret);
			exit(EXIT_FAILURE);
		}
	}

	/* create writers */
	for (i = 0; i < NUM_WRITERS; i++) {
		writer_stats[i].id = i + 1;
		writer_stats[i].iterations_completed = 0;
		ret = pthread_create(&writers[i], NULL, writer_thread,
				     &writer_stats[i]);
		if (ret != 0) {
			fprintf(stderr, "Failed to create writer %d: %d\n",
				i + 1, ret);
			exit(EXIT_FAILURE);
		}
	}

	/* stopping readers */
	for (i = 0; i < NUM_READERS; i++) {
		pthread_join(readers[i], NULL);
	}

	/* stopping writers*/
	for (i = 0; i < NUM_WRITERS; i++) {
		pthread_join(writers[i], NULL);
	}

	/* print stats */
	printf("\n=== USERSPACE STATISTICS ===\n");
	for (i = 0; i < NUM_READERS; i++) {
		printf("Reader %d completed %d/%d iterations\n", i,
		       reader_stats[i].iterations_completed, NUM_ITERATIONS);
	}
	for (i = 0; i < NUM_WRITERS; ++i) {
		printf("Writer %d completed %d/%d iterations\n", i,
		       writer_stats[i].iterations_completed, NUM_ITERATIONS);
	}
	printf("Final value of shared_data: %d\n",
	       atomic_load(&shared_counter));

	pthread_rwlock_destroy(&rw_lock);
	return EXIT_SUCCESS;
}