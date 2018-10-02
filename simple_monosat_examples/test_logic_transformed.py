#Import the MonoSAT library
from monosat import *


def bblogic(a, key):

	a0enc = Xnor(a[0], key[0])
	t0 = And(a0enc, a[1])
	t1 = And(a[0], a[2])
	t2 = And(a[1], a[2])
	t1enc = Xor(t1, key[1])
	t2enc = Xnor(t2, key[2])
	tobf = Or(t0, t1enc, t2enc)

	return tobf

def exclusions(a, list_ex):
	res = Var()
	if len(list_ex) > 0:
		print("hi")
		res = list_ex[0]
		return res
	else:
		return res


a = [None] * 3
key1 = [None] * 3
key2 = [None] * 3


for i in range(0, len(a)):
	a[i] = Var()

for i in range(0, len(key1)):
	key1[i] = Var()
	key2[i] = Var()

list_exclusions = []
list_exclusions.append(Not(And(Not(a[0]), Not(a[1]), Not(a[2]))))


Assert(Xor(bblogic(a, key1), bblogic(a, key2)))
Assert(exclusions(a, list_exclusions))


result = Solve() #Solve the instance in MonoSAT, return either True if the instance is SAT, and False if it is UNSAT
if result:
	print("SAT")
	print("a[0]: " + str(a[0].value()))
	print("a[1]: " + str(a[1].value())) 
	print("a[2]: " + str(a[2].value())) 
	print("key1[0]: " + str(key1[0].value())) 
	print("key1[1]: " + str(key1[1].value())) 
	print("key1[2]: " + str(key1[2].value())) 
	print("key2[0]: " + str(key2[0].value())) 
	print("key2[1]: " + str(key2[1].value())) 
	print("key2[2]: " + str(key2[2].value()))
else:
 	print("UNSAT")









# a0 = Var()
# a1 = Var() 
# a2 = Var()

# keyinput0A = Var()
# keyinput1A = Var()
# keyinput2A = Var()

# keyinput0B = Var()
# keyinput1B = Var()
# keyinput2B = Var()

# a0p0 = Var()
# a1p0 = Var() 
# a2p0 = Var()

# a0p1 = Var()
# a1p1 = Var() 
# a2p1 = Var()

# a0encA = Xnor(a0, keyinput0A)
# t0A = And(a0encA, a1)
# t1A = And(a0, a2)
# t2A = And(a1, a2)
# t1encA = Xor(t1A, keyinput1A)
# t2encA = Xnor(t2A, keyinput2A)
# tobfA = Or(t0A, t1encA, t2encA)

# a0encB = Xnor(a0, keyinput0B)
# t0B = And(a0encB, a1)
# t1B = And(a0, a2)
# t2B = And(a1, a2)
# t1encB = Xor(t1B, keyinput1B)
# t2encB = Xnor(t2B, keyinput2B)
# tobfB = Or(t0B, t1encB, t2encB)

# a0encp0A = Xnor(a0p0, keyinput0A)
# t0p0A = And(a0encp0A, a1p0)
# t1p0A = And(a0p0, a2p0)
# t2p0A = And(a1p0, a2p0)
# t1encp0A = Xor(t1p0A, keyinput1A)
# t2encp0A = Xnor(t2p0A, keyinput2A)
# tobfp0A = Or(t0p0A, t1encp0A, t2encp0A)

# a0encp0B = Xnor(a0p0, keyinput0B)
# t0p0B = And(a0encp0B, a1p0)
# t1p0B = And(a0p0, a2p0)
# t2p0B = And(a1p0, a2p0)
# t1encp0B = Xor(t1p0B, keyinput1B)
# t2encp0B = Xnor(t2p0B, keyinput2B)
# tobfp0B = Or(t0p0B, t1encp0B, t2encp0B)

# a0encp1A = Xnor(a0p1, keyinput0A)
# t0p1A = And(a0encp1A, a1p1)
# t1p1A = And(a0p1, a2p1)
# t2p1A = And(a1p1, a2p1)
# t1encp1A = Xor(t1p1A, keyinput1A)
# t2encp1A = Xnor(t2p1A, keyinput2A)
# tobfp1A = Or(t0p1A, t1encp1A, t2encp1A)

# a0encp1B = Xnor(a0p1, keyinput0B)
# t0p1B = And(a0encp1B, a1p1)
# t1p1B = And(a0p1, a2p1)
# t2p1B = And(a1p1, a2p1)
# t1encp1B = Xor(t1p1B, keyinput1B)
# t2encp1B = Xnor(t2p1B, keyinput2B)
# tobfp1B = Or(t0p1B, t1encp1B, t2encp1B)


# cmpwire = Xor(tobfA, tobfB)

# ap0 = And(Not(a0p0), Not(a1p0), Not(a2p0))
# ap1 = And(Not(a0p1), a1p1, Not(a2p1))


# #Add a unit clause to the solver, asserting that variable c must be true
# Assert(cmpwire)
# Assert(Not(tobfp0A))
# Assert(Not(tobfp0B))
# Assert(Not(tobfp1A))
# Assert(Not(tobfp1B))

# Assert(ap0)
# Assert(ap1)

# result = Solve() #Solve the instance in MonoSAT, return either True if the instance is SAT, and False if it is UNSAT
# if result:
# 	print("SAT")
# 	print("a0: " + str(a0.value()))
# 	print("a1: " + str(a1.value())) 
# 	print("a2: " + str(a2.value())) 
# 	print("keyinput0A: " + str(keyinput0A.value())) 
# 	print("keyinput1A: " + str(keyinput1A.value())) 
# 	print("keyinput2A: " + str(keyinput2A.value())) 
# 	print("keyinput0B: " + str(keyinput0B.value())) 
# 	print("keyinput1B: " + str(keyinput1B.value())) 
# 	print("keyinput2B: " + str(keyinput2B.value()))
# else:
# 	print("UNSAT")
