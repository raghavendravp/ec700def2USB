obj-m += writecatch.o

all:
	make -C /lib/modules/3.18.0-kali1-amd64/build M=$(PWD) modules

clean:
	make -C /lib/modules/3.18.0-kali1-amd64/build M=$(PWD) clean
