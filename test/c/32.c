#include "cachelab.h"

#include <getopt.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>

const char* usage = "Usage: %s [-hv] -s <s> -E <E> -b <b> -t <tracefile>\n";

int verbose = 0; //verbose flag
int s=-1;  //number of set index bits
int E=-1;  //number of lines per set
int b=-1;  //number of block bits
FILE* fp = NULL;

int hits = 0;
int misses = 0;
int evictions = 0;

#define HIT 1
#define MISS 2
#define EVICTION 3

typedef unsigned long uint64_t;

typedef struct {
    int valid;
    int lru;
    uint64_t tag;
} CacheLine;

typedef struct {
    // int E;
    CacheLine *cache_lines;
} CacheGroup;

typedef struct {
    // int S;
    CacheGroup *cache_groups;
} Cache;

void argparser(int argc, char* argv[]) {
    int opt;
    while ((opt = getopt(argc, argv, "hvs:E:b:t:")) != -1)
    {
        switch(opt)
        {
            case 'h':
                fprintf(stdout, usage, argv[0]);
                exit(1);
            case 'v':
                verbose = 1;
                break;
            case 's':
                s = atoi(optarg);
                break;
            case 'E':
                E = atoi(optarg);
                break;
            case 'b':
                b = atoi(optarg);
                break;
            case 't':
                fp = fopen(optarg, "r");
                break;
            default:
                fprintf(stdout, usage, argv[0]);
                exit(1);
        }
    }
    if (s == -1 || E == -1 || b == -1) {
        printf("s E b are required\n");
        exit(1);
    }
}

Cache* initCache() {
    // 根据s,E初始化cache
    int S = 1 << s;
    Cache *cache = malloc(sizeof(Cache));
    cache->cache_groups = calloc(S,sizeof(CacheGroup));
    for(int i=0;i<S;i++) {
        cache->cache_groups[i].cache_lines = (CacheLine*)calloc(E,sizeof(CacheLine));
    }
    return cache;
}

int visitCache(Cache *cache, uint64_t address) {

    uint64_t set_index = address >> b & ((1 << s) - 1);
    uint64_t tag = address >> (b+s);
    // printf("address = %lx, set_index = %lx, tag = %lx\n",address,set_index,tag);
    CacheGroup cache_group = cache->cache_groups[set_index];
    int evict = 0;
    int empty = -1;
    for(int i=0;i<E;i++) {
        if (cache_group.cache_lines[i].valid) {
            if (cache_group.cache_lines[i].tag == tag) {
                hits++;
                cache_group.cache_lines[i].lru = 1;
                return HIT;
            }
            cache_group.cache_lines[i].lru++;
            if (cache_group.cache_lines[evict].lru <= cache_group.cache_lines[i].lru) {
                evict = i;
            }
        } else {
            empty = i;
        }
    }
    misses++;
    if (empty != -1) {
        cache_group.cache_lines[empty].valid = 1;
        cache_group.cache_lines[empty].tag = tag;
        cache_group.cache_lines[empty].lru = 1;
        return MISS;
    } else {
        cache_group.cache_lines[evict].tag = tag;
        cache_group.cache_lines[evict].lru = 1;
        evictions++;
        return EVICTION;
    }
}

void simulate(Cache *cache) {

    char buf[30];
    char operation;
    uint64_t address;
    int size;
    int result;
    while (fgets(buf, sizeof(buf), fp) != NULL) {
        if (buf[0] == 'I') continue;
        sscanf(buf, " %c %lx,%d", &operation, &address, &size);
        result = visitCache(cache, address);
        if (operation == 'M') hits++;
        if (verbose) {
            switch (result) {
                case HIT:
                    printf("%c %lx,%d hit\n", operation, address, size);
                    break;
                case MISS:
                    printf("%c %lx,%d miss\n", operation, address, size);
                    break;
                case EVICTION:
                    printf("%c %lx,%d miss eviction\n", operation, address, size);
                    break;
                default:
                    fprintf(stdout, "unknown cache behave");
                    exit(1);
            }
        }
    }
    fclose(fp);
}

void freeCache(Cache* cache) {
    int S = 1<<s;
    for(int i=0;i<S;i++) {
        free(cache->cache_groups[i].cache_lines);
    }
    free(cache->cache_groups);
    free(cache);
}

int main(int argc, char **argv)
{
    argparser(argc,argv);
    Cache *cache = initCache();
    simulate(cache);
    freeCache(cache);
    printSummary(hits, misses, evictions);
    return 0;
}
