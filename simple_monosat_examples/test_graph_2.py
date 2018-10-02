#Import the MonoSAT library
from monosat import *
g= Graph()

a0 = g.addNode("a0") #0
a1 = g.addNode("a1") #1
a2 = g.addNode("a2") #2
k0 = g.addNode("k0") #3
k1 = g.addNode("k1") #4
k2 = g.addNode("k2") #5
a0enc = g.addNode("a0enc") #6 
a0encd1 = g.addNode("a0encd1") #7
a0encd2 = g.addNode("a0encd2") #8
t0 = g.addNode("t0") #9
t1 = g.addNode("t1") #10
t2 = g.addNode("t2") #11
t1enc = g.addNode("t1enc") #12
t1encd = g.addNode("t1encd") #13
t2enc = g.addNode("t2enc") #14
t2encd = g.addNode("t2encd") #15
obf = g.addNode("obf") #16

keyinput3 = Var()
keyinput4 = Var()
keyinput5 = Var()


e0 = g.addEdge(a0,a0enc,2) 
e1 = g.addEdge(k0,a0enc,2)
k30 = g.addEdge(a0enc,a0encd1,5)
k31 = g.addEdge(a0enc,a0encd2,10)
e121 = g.addEdge(a0encd1,t0,2)
e122 = g.addEdge(a0encd2,t0,2)
e3 = g.addEdge(a1,t0,2)

e2 = g.addEdge(a0,t1,2)
e6 = g.addEdge(a2,t1,2)
e13 = g.addEdge(t1,t1enc,2)
e5 = g.addEdge(k1,t1enc,2)
k40 = g.addEdge(t1enc,t1encd,10)
k41 = g.addEdge(t1enc,t1encd,5)

e4 = g.addEdge(a1,t2,2)
e7 = g.addEdge(a2,t2,2)
e9 = g.addEdge(t2,t2enc,2)
e8 = g.addEdge(k2,t2enc,2)
k50 = g.addEdge(t2enc,t2encd,5)
k51 = g.addEdge(t2enc,t2encd,10)

e10 = g.addEdge(t0, obf, 3)
e11 = g.addEdge(t1encd, obf, 3)
e14 = g.addEdge(t2encd, obf, 3)

lowerbound = g.distance_leq(a0,obf,20)
Assert(lowerbound)
result = Solve()

upperbound = ~g.distance_leq(a0,obf,15)
Assert(upperbound)
result = Solve()



print(result)

if result:
    #If the result is SAT, you can find the nodes that make up a satisfying path:
    path_by_nodes = g.getPath(upperbound)
    print("Satisfying path (as a list of nodes): " +str(path_by_nodes))
    #You can also list the edge literals that make up that path
    path_by_edges = g.getPath(upperbound,return_edge_lits=True)
    for e in path_by_edges:
        v = e.value()
        assert(v)
    print("Satisfying path (as a list of nodes): " +str(path_by_edges))
