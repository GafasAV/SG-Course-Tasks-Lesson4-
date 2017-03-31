import threading
import time
import random

__author__ = "Adrew Gafiychuk"


def worker(file):
    thread_name = threading.current_thread().name

    try:
        fileAccess.acquire()

        file.write("{name}: started.\n".format(name=thread_name))
        time.sleep(random.random() * 5)
        file.write("{name}: done.\n".format(name=thread_name))
    finally:
        fileAccess.release()


if __name__ == "__main__":
    file = open("test.txt", "a")

    fileAccess = threading.RLock()

    threads = []

    for i in range(1, 11):
        tname = "Thread {0}".format(i)
        thread = threading.Thread(target=worker, name=tname, args=(file,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    count = threading.activeCount()
    if count == 1:
        print("Tasks done... Exiting...")

    file.close()