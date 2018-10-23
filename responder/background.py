import traceback
import multiprocessing
import concurrent.futures


class BackgroundQueue:
    def __init__(self, n=None):
        if n is None:
            n = multiprocessing.cpu_count()

        self.n = n
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=n)
        self.results = []

    def run(self, f, *args, **kwargs):
        self.pool._max_workers = self.n
        self.pool._adjust_thread_count()

        f = self.pool.submit(f, *args, **kwargs)
        self.results.append(f)
        return f

    def task(self, on_success=None, on_exception=None):

        def done_callback(fs):
            try:
                res = fs.result()
                if on_success:
                    on_success(res)
            except Exception as error:
                if on_exception:
                    on_exception(error)
                else:
                    traceback.print_exc()

        def decorator_do_task(f):
            def do_task(*args, **kwargs):
                result = self.run(f, *args, **kwargs)
                result.add_done_callback(done_callback)
                return result

            return do_task
        return decorator_do_task
