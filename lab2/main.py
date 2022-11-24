from sys import getsizeof
from time import time, sleep


class CachceWrapper:
    def __init__(self, max_count=100, max_size=10000, ttl=60, has_logs=False) -> None:
        self.cache = {}
        self.queue = []
        self.max_count = max_count
        self.max_size = max_size
        self.ttl = ttl
        self.has_logs = has_logs

    def __call__(self, f) -> callable:
        def wrapper(*args, **kwargs):          
            removed_keys = self._clean_cache()
            if self.has_logs and len(removed_keys) > 0:
                print(f'removed from cache {removed_keys} for {f.__name__}')

            kwtuple = tuple((key, kwargs[key]) for key in sorted(kwargs.keys()))
            key = (args, kwtuple)

            if key in self.cache:
                if self.has_logs:
                    print(f'got value for {f.__name__} with args:{args} and kwargs:{kwargs} from cache; in cache: {self.cache}')
                return self.cache[key]

            value = f(*args, **kwargs)
            if len(self.cache) < self.max_count and getsizeof(value) + self._calc_size() < self.max_size:
                if self.has_logs:
                    print(f'store value for {f.__name__} with args:{args} and kwargs:{kwargs} from cache; in cache: {self.cache}')
                self.cache[key] = value
                self.queue.append((key, time()))

            return value
        return wrapper

    def _calc_size(self) -> int:
        total_size = 0
        for _, v in self.cache.items():
            total_size += getsizeof(v)
        return total_size

    def _clean_cache(self) -> list:
        removed_keys = []

        now = time()
        for item in self.queue:
            if self.ttl + item[1] < now:
                removed_keys.append(item[0])

                self.cache.pop(item[0])
                self.queue = self.queue[1:]
            else:
                break
        
        return removed_keys


@CachceWrapper(has_logs=True, max_size=0)
def sum(a, b):
    return a + b

@CachceWrapper(has_logs=True, max_count=1, ttl=2)
def multiply(a, b):
    return a * b

print(sum(1, 2))
print(multiply(1, 2))
print(sum(3, 4))
print(multiply(5, 7))
print(sum(5, 7))
print(multiply(1, 2))
sleep(5)
print(sum(3, 4))
print(multiply(5, 7))
