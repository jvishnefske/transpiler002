# file to parse, and attempt to create python
import ctypes


def square(a: ctypes.c_int32) -> ctypes.c_int32:
    return a * a


def main():
    b = 1
    b = b + 1
    print(square(2))


if __name__ == "__main__":
    main()
