// sloppy-counter.c
// Naive sloppy counter that WILL incur false sharing.
// Now supports: configurable flush threshold + configurable worker count.

#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define SLOTS_COUNT 101   // very small → causes slot collisions

struct sloppy_counter_t {
    atomic_int global;
    int flush_threshold;     // configurable
    int lcounters[SLOTS_COUNT];   // contiguous → false sharing guaranteed
};

// ------------------------------------------------------------
// Initialization
// ------------------------------------------------------------
void sloppy_init(struct sloppy_counter_t *c, int threshold) {
    atomic_store(&c->global, 0);

    if (threshold <= 0)
        threshold = 128;

    c->flush_threshold = threshold;

    for (int i = 0; i < SLOTS_COUNT; i++)
        c->lcounters[i] = 0;
}

// ------------------------------------------------------------
// Slot selection (naive, hash pthread ID)
// ------------------------------------------------------------
static int slot_id(pthread_t tid) {
    uint64_t v = 0;
    memcpy(&v, &tid, sizeof(tid) < sizeof(v) ? sizeof(tid) : sizeof(v));
    return (int)(v % SLOTS_COUNT);
}

// ------------------------------------------------------------
// Increment (false-sharing-prone)
// ------------------------------------------------------------
void sloppy_increment(struct sloppy_counter_t *c, pthread_t tid) {
    int sid = slot_id(tid);
    c->lcounters[sid]++;

    if (c->lcounters[sid] >= c->flush_threshold) {
        atomic_fetch_add(&c->global, c->lcounters[sid]);
        c->lcounters[sid] = 0;
    }
}

// ------------------------------------------------------------
void sloppy_flush_thread(struct sloppy_counter_t *c, pthread_t tid) {
    int sid = slot_id(tid);
    int v = c->lcounters[sid];

    if (v > 0) {
        atomic_fetch_add(&c->global, v);
        c->lcounters[sid] = 0;
    }
}

// ------------------------------------------------------------
void sloppy_flush_all(struct sloppy_counter_t *c) {
    for (int i = 0; i < SLOTS_COUNT; i++) {
        int v = c->lcounters[i];
        if (v > 0) {
            atomic_fetch_add(&c->global, v);
            c->lcounters[i] = 0;
        }
    }
}

// ------------------------------------------------------------
int sloppy_get(struct sloppy_counter_t *c) {
    int total = atomic_load(&c->global);
    for (int i = 0; i < SLOTS_COUNT; i++)
        total += c->lcounters[i];
    return total;
}



static struct sloppy_counter_t g_counter;

void *worker(void *arg) {
    (void)arg;
    pthread_t tid = pthread_self();

    for (int i = 0; i < 1000000; i++)
        sloppy_increment(&g_counter, tid);

    sloppy_flush_thread(&g_counter, tid);
    return NULL;
}

int main(int argc, char **argv) {
    int threshold = 128;
    int workers   = 8;   // default

    if (argc >= 2)
        threshold = atoi(argv[1]);

    if (argc >= 3)
        workers = atoi(argv[2]);

    printf("Using flush threshold = %d, workers = %d\n", threshold, workers);

    sloppy_init(&g_counter, threshold);

    pthread_t *ths = malloc(sizeof(pthread_t) * workers);

    for (int i = 0; i < workers; i++)
        pthread_create(&ths[i], NULL, worker, NULL);

    for (int i = 0; i < workers; i++)
        pthread_join(ths[i], NULL);

    sloppy_flush_all(&g_counter);

    printf("Final count = %d (expected %d)\n",
           sloppy_get(&g_counter),
           workers * 1000000);

    free(ths);
    return 0;
}

