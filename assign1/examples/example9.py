# Fibonacci sequence
a = 1
b = 1

# Iteration 1
c = a
a = b
b = c + b

# Iteration 2
c = a
a = b
b = c + b

# Iteration 3
c = a
a = b
b = c + b

# Now a = 5, b = 8
# Cassini's Identity: b*b - a*a - a*b = (-1)**n
# Here n=4, so b*b - a*a - a*b = 1
assert b*b - a*a - a*b == 1