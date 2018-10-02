#Import the MonoSAT library
from monosat import *
g= Graph()
e0 = g.addEdge(0,1) 
e1 = g.addEdge(1,2)
e2 = g.addEdge(2,8)
e3 = g.addEdge(0,3)
e4 = g.addEdge(3,8)
e5 = g.addEdge(0,4)
e6 = g.addEdge(4,5)
e7 = g.addEdge(5,6)
e8 = g.addEdge(6,7)
e9 = g.addEdge(7,8)


g.draw()

lowerbound = g.distance_leq(0,8,10000)
Assert(lowerbound)
result = Solve()

upperbound = ~g.distance_leq(0,8,3)
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
