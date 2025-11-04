def inc(x):
    requires(True)
    ensures(x == x_old + 1)
    x = x + 1

x = 0
inc(x)
assert(x == 1)

