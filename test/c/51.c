static void type_initialize(TypeImpl *ti)
{
    // ...
    if (ti->class_init) {
        ti->class_init(ti->class, ti->class_data);
    }
    t->f1()->f2();
    t.x.f1()->x.f2();
}

static void object_class_foreach_tramp(gpointer key, gpointer value,
                                       gpointer opaque)
{
    OCFData *data = opaque;
    TypeImpl *type = value;
    ObjectClass *k;

    type_initialize(type);
    k = type->class;

    if (!data->include_abstract && type->abstract) {
        return;
    }

    if (data->implements_type &&
        !object_class_dynamic_cast(k, data->implements_type)) {
        return;
    }

    data->fn(k, data->opaque);
}