// super_baseline.c
// Super-naive baseline: all workers increment the SAME global atomic counter.
// This is intentionally slow to show heavy contention.

#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static atomic_int global_counter; 

struct worker_arg {
    int dummy;
};

// ------------------------------------------------------------
void *worker(void *arg) {
    (void)arg;
    for (int i = 0; i < 1000000; i++) {
        atomic_fetch_add(&global_counter, 1);
    }
    return NULL;
}

// ------------------------------------------------------------
int main(int argc, char **argv) {
    int workers = 8; 

    if (argc >= 2)
        workers = atoi(argv[1]);

    printf("Running super baseline: workers = %d\n", workers);

    atomic_store(&global_counter, 0);

    pthread_t *threads = malloc(sizeof(pthread_t) * workers);

    for (int i = 0; i < workers; i++)
        pthread_create(&threads[i], NULL, worker, NULL);

    for (int i = 0; i < workers; i++)
        pthread_join(threads[i], NULL);

    printf("Final count = %d (expected %d)\n",
           atomic_load(&global_counter),
           workers * 1000000);

    free(threads);
    return 0;
}
