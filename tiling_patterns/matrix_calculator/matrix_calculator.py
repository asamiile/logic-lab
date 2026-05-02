def mult_mtx(mtx1: list[list[int]], mtx2: list[list[int]]) -> list[list[int]]:
    new_mtx = [[0 for _ in range(len(mtx2[0]))] for _ in range(len(mtx1))]
    for i in range(len(mtx1)):
        for j in range(len(mtx2[0])):
            total = 0
            for k in range(len(mtx2)):
                total += mtx1[i][k] * mtx2[k][j]
            new_mtx[i][j] = total
    return new_mtx


def tr_mtx(mtx: list[list[int]]) -> list[list[int]]:
    return [[mtx[i][j] for i in range(len(mtx))] for j in range(len(mtx[0]))]


def print_mtx(label: str, mtx: list[list[int]]) -> None:
    print(label)
    for i, row in enumerate(mtx):
        print(f"row:{i}")
        print(row)


def main() -> None:
    mtx_a = [[2, 1], [0, 1]]
    mtx_b = [[3], [1]]
    print_mtx("mult:", mult_mtx(mtx_a, mtx_b))
    print_mtx("transpose:", tr_mtx(mtx_a))


if __name__ == "__main__":
    main()

