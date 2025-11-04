# { i != j }
assume(i != j)

a[i] = v
assert(a[j] == old(a)[j])


