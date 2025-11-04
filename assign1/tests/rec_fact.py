def fact(n):
    requires(n >= 0)
    ensures((n == 0 and ret == 1) or (n > 0 and ret > 0))
    if n == 0:
        return 1
    else:
        t = fact(n - 1)
        return n * t

