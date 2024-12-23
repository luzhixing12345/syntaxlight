enum pageflags {
    PG_locked,    /* Page is locked. Don't touch. */
    PG_writeback, /* Page is under writeback */
    PG_referenced,
    PG_uptodate,
    PG_dirty,
    PG_lru,
    ...,
    PG_head,    /* Must be in bit 6 */
    PG_waiters, /* Page has waiters, check its waitqueue. Must be bit #7 and in the same byte as "PG_locked" */
    PG_active,
    PG_workingset,
    PG_reserved,
    PG_reclaim,     /* To be reclaimed asap */
    PG_swapbacked,  /* Page is backed by RAM/swap */
    PG_unevictable, /* Page is "unevictable"  */
    ...
};

enum X {
    abc,
    ...
    def
};