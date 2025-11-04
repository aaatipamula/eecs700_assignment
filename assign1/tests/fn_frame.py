def change_x():
    requires(True)
    ensures(x == x_old + 1)
    x = x + 1
    return x

x = 3
change_x()
assert(x == 4)

