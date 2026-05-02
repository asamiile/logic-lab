def euclidean_algorithm(a: int, b: int) -> int:
    d = b
    itr = 0

    while d > 0:
        itr += 1
        c = a // b
        d = a % b
        print(itr, ":", a, "/", b, "=", c, "...", d)
        a = b
        b = d

    print("GCD is", a)
    return a


if __name__ == "__main__":
    euclidean_algorithm(10, 6)

