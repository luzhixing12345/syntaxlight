#define QTAILQ_FOREACH() 1

void module_call_init(module_init_type type)
{
    QTAILQ_FOREACH(e, l, node) {
        e->init();
    }

    modules_init_done[type] = true;
}