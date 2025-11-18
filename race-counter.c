// race_counter.c

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

static volatile long long counter = 0;   // volatile prevents register caching

struct thread_arg {
    int iters;
};

void *worker(void *arg) {
    struct thread_arg *ta = (struct thread_arg *)arg;
    int iters = ta->iters;

    for (int i = 0; i < iters; i++) {
        // compiler barrier prevents reordering or collapsing the loop
        asm volatile("" ::: "memory");

        counter++;    // (race condition)
    }

    return NULL;
}

int main(int argc, char **argv) {
    int workers = 4;     // default
    int iters = 100000;  // increments per worker

    if (argc >= 2)
        workers = atoi(argv[1]);

    printf("Running race-condition demo with %d workers...\n\n", workers);

    for (int run = 0; run < 100; run++) {
        counter = 0;

        pthread_t *threads = malloc(sizeof(pthread_t) * workers);
        struct thread_arg ta = { .iters = iters };

        for (int i = 0; i < workers; i++)
            pthread_create(&threads[i], NULL, worker, &ta);

        for (int i = 0; i < workers; i++)
            pthread_join(threads[i], NULL);

        long long expected = (long long)workers * iters;
        printf("Run %3d: counter = %lld  (expected %lld)\n",
               run + 1, counter, expected);

        free(threads);
    }

    return 0;
}
