def bump(x):
  requires(True)
  ensures(ret == x_old + 1)
  return x + 1
