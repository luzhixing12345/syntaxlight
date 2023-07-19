int32_t List_GetCount(List *me)
{
    return me->count;
}

int32_t List_Remove(List *me, ListElement *elem, void **data)
{
    if (elem == NULL || me->count == 0)
        return -1;

    if (data != NULL)
        *data = elem->data;

    if (elem == me->head)
    {
        me->head = elem->next;

        if (me->head == NULL)
        {
            me->tail = NULL; /* No element left */
        }
        else
        {
            me->head->prev = NULL;
        }
    }
    else
    {
        assert(elem == elem->prev->next);

        elem->prev->next = elem->next;

        if (elem->next == NULL)
        {
            me->tail = elem->prev; /* Removing tail element */
        }
        else
        {
            elem->next->prev = elem->prev;
        }
    }

    free(elem);
    me->count--;

    return 0;
}

void List_AddData(List *me, const void *data)
{
    ListElement *elem = malloc(sizeof(ListElement));
    assert(elem != NULL);

    if (me->head == NULL)
    {
        me->head = elem;
        elem->prev = NULL;
    }
    else
    {
        elem->prev = me->tail;
        elem->prev->next = elem;
    }

    me->tail = elem;
    elem->data = (void*) data;
    elem->next = NULL;

    me->count++;
}

bool List_ContainsData(const List *me, const void *data)
{
    bool ret = false;

    for (ListElement *i = me->head; i != NULL; i = i->next)
    {
        if (i->data == data)
        {
            ret = true;
            break;
        }
    }

    return ret;
}

int32_t List_RemoveData(List *me, const void *data)
{
    int32_t ret = -1;

    for (ListElement *i = me->head; i != NULL; i = i->next)
    {
        if (i->data == data)
        {
            List_Remove(me, i, NULL);
            ret = 0;
            break;
        }
    }

    return ret;
}