def sum(a, n):
    requires(n >= 0)
    ensures(ret >= 0)
    if n == 0:
        return 0
    else:
        t = sum(a, n - 1)
        return t + a[n - 1]

