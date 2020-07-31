from concurrent.futures import ThreadPoolExecutor
import random
import time
import threading


semaphore = threading.Semaphore(3)


def wait_random():
    thread_id = threading.get_ident()
    to_wait = random.randint(1, 10)
    with semaphore:
        print(f"Thread {thread_id:5d}: Waiting {to_wait:2d} seconds")
        start_time = time.time()
        time.sleep(to_wait)

        end_time = time.time()
        elapsed = end_time - start_time
        print(
            f"Thread {thread_id:5d}: Resumed after {elapsed:3.3f} seconds"
        )


if __name__ == "__main__":
    with ThreadPoolExecutor() as pool:
        # Schedule two worker functions
        for i in range(5):
            pool.submit(wait_random)
