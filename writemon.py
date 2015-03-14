import sys, subprocess, socket, datetime

DIR_TO_WATCH = "/media/"

def taint(fp):
	output = subprocess.check_output(["chattr", "+d", fp])

def istainted(fp):
	output = subprocess.check_output(["lsattr", fp])
	if "d" in output.split(" ")[0]:
		return True

	return False

def hashfile(fp):
	output = subprocess.check_output(["sha1sum", fp])
	return output.split(" ")[0]

#for l in sys.stdin:
for l in iter(sys.stdin.readline, ''):
	if len(l.split(">")) > 1:
		l = l.strip().split(">")[1]
		if l.startswith("Write"):
			l = l.split(",")
			wp = l[1]
			exe = l[2]
			if "(deleted)" in wp:
				continue 
			try:		

				if exe.startswith(DIR_TO_WATCH) or istainted(exe):
					print ",".join([wp, hashfile(wp), exe, hashfile(exe), socket.gethostname(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

					taint(wp)
				elif wp.startswith(DIR_TO_WATCH):
					print ",".join([wp, hashfile(wp), exe, hashfile(exe), socket.gethostname(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

			except:
				pass



