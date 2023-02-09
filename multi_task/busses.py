from readerwriterlock import rwlock


class Busses(object):
    def __init__(self):
        # Init lock and clear message
        self.lock = rwlock.RWLockWriteD()
        self.message = None

    def write(self, data):
        # Write data under the lock
        with self.lock.gen_wlock():
            self.message = data

    def read(self):
        # Read data under the lock
        with self.lock.gen_rlock():
            data = self.message
        return data
