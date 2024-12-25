import pdb

# Your script code here
print("This is a script in debug mode.")


class MyIter:
    def __init__(self):
        self._start = 0

    def __iter__(self):
        return iter([1, 2, 3])

    def __next__(self):
        if self._start < 10:
            self._start += 1
            return self._start
        else:
            raise StopIteration


if __name__ == "__main__":

    a = MyIter()
    for i in a:
        print(i)

    # Set a breakpoint
    pdb.set_trace()
