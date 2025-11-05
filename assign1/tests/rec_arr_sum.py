def sum(n):
    requires(n >= 0)
    ensures(ret >= 0)
    if n == 0:
        return 0
    else:
        t = sum(n - 1)
        return n + t

