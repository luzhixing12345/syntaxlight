
/*
 * Tail queue definitions.  The union acts as a poor man template, as if
 * it were QTailQLink<type>.
 */
#define QTAILQ_HEAD(name, type)                                         \
union name {                                                              \
        struct type *tqh_first;       /* first element */               \
        QTailQLink tqh_circ;          /* link for circular backwards list */ \
}

#define X 1

struct QemuOptsList {
    const char *name;
    const char *implied_opt_name;
    bool merge_lists;  /* Merge multiple uses of option into a single list? */
    X x;
    QTAILQ_HEAD(, QemuOpts) head;
    QemuOptDesc desc[];
};