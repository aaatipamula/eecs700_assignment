def inc(x):
  requires(x >= 0)
  ensures(ret == x_old + 1)
  x = x + 1
  return x

