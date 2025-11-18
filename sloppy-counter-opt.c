// sloppy-counter-opt.c
// False-sharing-free counter with minimal design.
// No sched_getcpu(), no TLS registration function.
// Each worker gets a unique shard ID directly.

#define _GNU_SOURCE
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef CACHELINE_SIZE
#define CACHELINE_SIZE 64
#endif

#ifndef MAX_SHARDS
#define MAX_SHARDS 128
#endif

// ------------------------------------------------------------
// Each shard sits in its own exclusive cacheline.
// ------------------------------------------------------------
struct counter_shard {
    int local;
    char pad[CACHELINE_SIZE - sizeof(int)];
};

// ------------------------------------------------------------
struct sloppy_counter_t {
    atomic_int global;
    int flush_threshold;
    struct counter_shard shards[MAX_SHARDS];
};

// ------------------------------------------------------------
void sloppy_init(struct sloppy_counter_t *c, int threshold) {
    atomic_store(&c->global, 0);
    c->flush_threshold = (threshold > 0 ? threshold : 128);

    for (int i = 0; i < MAX_SHARDS; i++)
        c->shards[i].local = 0;
}

// ------------------------------------------------------------
void sloppy_increment(struct sloppy_counter_t *c, int shard_id) {
    struct counter_shard *s = &c->shards[shard_id];

    s->local++;

    if (s->local >= c->flush_threshold) {
        atomic_fetch_add(&c->global, s->local);
        s->local = 0;
    }
}

// ------------------------------------------------------------
void sloppy_flush_thread(struct sloppy_counter_t *c, int shard_id) {
    struct counter_shard *s = &c->shards[shard_id];
    int v = s->local;

    if (v > 0) {
        atomic_fetch_add(&c->global, v);
        s->local = 0;
    }
}

// ------------------------------------------------------------
void sloppy_flush_all(struct sloppy_counter_t *c) {
    for (int i = 0; i < MAX_SHARDS; i++) {
        int v = c->shards[i].local;
        if (v > 0) {
            atomic_fetch_add(&c->global, v);
            c->shards[i].local = 0;
        }
    }
}

// ------------------------------------------------------------
int sloppy_get(struct sloppy_counter_t *c) {
    int total = atomic_load(&c->global);
    for (int i = 0; i < MAX_SHARDS; i++)
        total += c->shards[i].local;
    return total;
}


static struct sloppy_counter_t g_counter;

struct worker_arg {
    int shard_id;
};

void *worker(void *arg) {
    int shard_id = *(int *)arg;

    for (int i = 0; i < 1000000; i++)
        sloppy_increment(&g_counter, shard_id);

    sloppy_flush_thread(&g_counter, shard_id);
    return NULL;
}

int main(int argc, char **argv) {
    int threshold = 128;
    int workers   = 8;

    if (argc >= 2) threshold = atoi(argv[1]);
    if (argc >= 3) workers   = atoi(argv[2]);

    printf("Using flush threshold = %d, workers = %d\n",
           threshold, workers);

    sloppy_init(&g_counter, threshold);

    pthread_t *threads = malloc(sizeof(pthread_t) * workers);
    int *ids = malloc(sizeof(int) * workers);

    for (int i = 0; i < workers; i++) {
        ids[i] = i;   // directly use worker index as shard ID
        pthread_create(&threads[i], NULL, worker, &ids[i]);
    }

    for (int i = 0; i < workers; i++)
        pthread_join(threads[i], NULL);

    sloppy_flush_all(&g_counter);

    printf("Final count = %d (expected %d)\n",
           sloppy_get(&g_counter),
           workers * 1000000);

    free(ids);
    free(threads);
    return 0;
}
