// super_baseline_mutex.c
// Super naive baseline using a SINGLE mutex around a SINGLE shared counter.
// This model intentionally maximizes contention.

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

static int global_counter = 0;
static pthread_mutex_t counter_lock = PTHREAD_MUTEX_INITIALIZER;

// ------------------------------------------------------------
void *worker(void *arg) {
    (void)arg;

    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&counter_lock);
        global_counter++;
        pthread_mutex_unlock(&counter_lock);
    }

    return NULL;
}

// ------------------------------------------------------------
int main(int argc, char **argv) {
    int workers = 8; // default

    if (argc >= 2) {
        workers = atoi(argv[1]);
        if (workers <= 0) workers = 1;
    }

    printf("Running SUPER-NAIVE MUTEX baseline: workers = %d\n", workers);

    global_counter = 0;

    pthread_t *threads = malloc(sizeof(pthread_t) * workers);

    for (int i = 0; i < workers; i++)
        pthread_create(&threads[i], NULL, worker, NULL);

    for (int i = 0; i < workers; i++)
        pthread_join(threads[i], NULL);

    printf("Final count = %d (expected %d)\n",
           global_counter,
           workers * 1000000);

    free(threads);
    return 0;
}
