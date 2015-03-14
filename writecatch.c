#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/delay.h>
#include <asm/paravirt.h>

#include <linux/limits.h>
#include <linux/file.h>
#include <linux/fs.h>
#include <linux/fdtable.h>
//#include <linux/fcntl.h>
//#include <linux/unistd.h>
//#include <linux/stat.h>
//#include <linux/types.h>
//#include <bits/stdlib.h>

#include <linux/unistd.h>


//for kmalloc
#include<linux/slab.h>



unsigned long **sys_call_table;
unsigned long original_cr0;



asmlinkage long (*ref_sys_write)(unsigned int fd, const char __user *buf, size_t count);
asmlinkage long new_sys_write(unsigned int fd, const char __user *buf, size_t count)
{

	long ret;
	


	struct file * filep;  

	struct files_struct *files;
	struct path f_path;
	//struct dentry * d_entry_exe;
	char * wpathp;
	char * epathp;

	int pathlen = 100;

	char * unwatched_dir1 = "/var/";
	char * unwatched_dir2 = "/dev/";
	char * unwatched_dir3 = "/run/";
	
	char write_path [pathlen];

	struct file * exe_file;
	struct mm_struct *mm;
	char exe_path [pathlen];

	//actually perform the write
	ret = ref_sys_write(fd, buf, count);

	//short circuit output if this is kernel business
	if (current->pid == 0 || current->pid == 1) return ret;


	//find the path of the file to be written	
	files = current->files;
	filep = fcheck_files(files, fd);
	f_path = filep->f_path;

	wpathp = d_path(&f_path, write_path, pathlen*sizeof(char) );

	//we ignore var list writting to avoid an infinite write loop
	if (strlen(wpathp) < strlen(unwatched_dir1) ) return ret;

	if( strncmp(wpathp, unwatched_dir1, strlen(unwatched_dir1)) == 0 ||
	    strncmp(wpathp, unwatched_dir2, strlen(unwatched_dir2)) == 0 ||
	    strncmp(wpathp, unwatched_dir3, strlen(unwatched_dir3)) == 0
            ) return ret;

	if ( wpathp[0] == '/' ) {
		
		//lets find the process executable path	
		//straight up stolen from get_mm_exe_file	
		mm = get_task_mm(current);
		down_read(&mm->mmap_sem); //lock read
		exe_file = mm->exe_file;
		if (exe_file) get_file(exe_file);
		up_read(&mm->mmap_sem); //unlock read

		//reduce exe path to a string
		epathp = d_path( &(exe_file->f_path), exe_path, pathlen*sizeof(char) );

	  	printk(KERN_INFO ">Write,%s,%s,%d\n", wpathp, epathp, current->pid);
	}


	return ret;
}



//I did not write this, but rather found it on the internet.
static unsigned long **aquire_sys_call_table(void)
{
	unsigned long int offset = PAGE_OFFSET;
	unsigned long **sct;

	while (offset < ULLONG_MAX) {
		sct = (unsigned long **)offset;

		if (sct[__NR_close] == (unsigned long *) sys_close) 
			return sct;

		offset += sizeof(void *);
	}
	
	return NULL;
}

static int __init interceptor_start(void) 
{
	//printk(KERN_INFO "intercept set1: 0x");
	if(!(sys_call_table = aquire_sys_call_table()))
		return -1;
	
	original_cr0 = read_cr0();

	write_cr0(original_cr0 & ~0x00010000);
	ref_sys_write = (void *)sys_call_table[__NR_write];
	sys_call_table[__NR_write] = (unsigned long *)new_sys_write;
	write_cr0(original_cr0);
	//printk(KERN_INFO "intercept set2: 0x");
	

	return 0;
}

static void __exit interceptor_end(void) 
{

	//printk(KERN_INFO "intercept done1: 0x");
	if(!sys_call_table) {
		return;
	}
	
	write_cr0(original_cr0 & ~0x00010000);
	sys_call_table[__NR_write] = (unsigned long *)ref_sys_write;
	write_cr0(original_cr0);
	
	msleep(2000);
}

module_init(interceptor_start);
module_exit(interceptor_end);

MODULE_LICENSE("GPL");
