assume(x >= 0)
assume(y > 0)
q = x / y
r = x - q * y
assert r >= 0
assert r < y
