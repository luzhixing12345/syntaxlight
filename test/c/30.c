// 注释信息
#include <linux/init.h>
#include <linux/module.h>

static int major = 237;
static int minor = 0;
static dev_t devno;


static int hello_open (struct inode *inode, struct file *filep)
{
    printk("hello_open()\n");
    return 0;
}
static int hello_release (struct inode *inode, struct file *filep)
{
    printk("hello_release()\n");
    return 0;
}

#define KMAX_LEN 32
char kbuf[KMAX_LEN+1] = "kernel";
//write(fd,buff,40);
static ssize_t hello_write (struct file *filep, const char __user *buf, size_t size, loff_t *pos)
{
    int error;
    if(size > KMAX_LEN)
    {
        size = KMAX_LEN;
    }
    memset(kbuf,0,sizeof(kbuf));
    if(copy_from_user(kbuf, buf, size))
    {
        error = -EFAULT;
        return error;
    }
    printk("%s\n",kbuf);
    return size;
}

Agsym_t *sym = agattr(g,AGNODE,"shape","box");
char *str = agxget(n,sym);
agxset(n,sym,"hexagon");

typedef struct mynode_s {
    Agrec_t h;
    int count;
} mynode_t;
mynode_t *data;
Agnode_t *n;
n = agnode(g, "mynodename", TRUE);
data = (mynode_t *)agbindrec(n, "mynode_t", sizeof(mynode_t), FALSE);
data->count = 1;