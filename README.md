# SMT Tool
SMT tool is a SAT Module Theory solver based attack on logic locking. 
SMT attack provides Boolean SAT solver as well as non-Boolean theory solvers, such as graph theory solver. 
All the algorithms and functions work on .BENCH format. 

The current version of the tool supports the following attack algorithms: 

- [Reduced SAT Attack]: SMT reduced to SAT working on all Boolean logic locking techniques.
- [Eager SMT Attack]: Eager-based SMT-solver-based attack on DLL (delay and logic locking).
- [Lazy SMT Attack]: Lazy-based SMT-solver-based attack on DLL (delay and logic locking).
- [Approximate SMT Attack]: Double-Dip-based approximate attack using SMT solver.
- [Hamming-based SMT Attack]: SAT-based attack using SMT solver with BitVector theory solver to prioritize DIPs with more hamming distance.
- [Limited Reduced SAT Attack]: SMT reduced to SAT working on all Boolean logic locking techniques with pre-determined numbner of iteration.
- [Limited Reduced Hamming SMT Attack]: Hamming distance based SAT attack on compound logic locking with pre-determined numbner of iterations.

Also, in SMT tool, some well-known logic locking techniques are already implemented and could be used for any form of evaluation. 

- [Random]: Random-based logic locking by inserting XOR gates.
- [SARLock]: SARLock technique (point function using flipping circuitry).

### Building
SMT tool is implemented in Python, and it is compatible with Python>=3.0. 

*[MonoSAT]* is embedded in the SMT tool to provide the theory solvers. MonoSAT is Z3-inspired Python 3 interface and provides a SAT Modulo Theory solver for *[monotonic theories]*. It supports a wide set of graph predicates (including reachability, shortest paths, maximum *s-t* flow, minimum spanning tree, and acyclicity constraints). MonoSAT also has limited support for geometric constraints involving convex hulls of point sets, and experimental support for constraints on finite state machines. The main steps of the buidling this package is also added here. 

Please run the following commands to install the SMT tool on your machine. 

```
sudo apt update
sudo apt update
```

You can directly clone MonoSAT package from its repository. 

```
git clone https://github.com/sambayless/monosat
```

MonoSAT requires CMake (version 2.7 or higher). Also, SMT tool requires Python library of the MonoSAT. MonoSAT also requires ZLIB and GMP. 

```
sudo apt-get install zlib1g-dev
sudo apt-get install libgmp-dev
cd monosat
cmake -DPYTHON=ON .
make
sudo make install
```

### Simple Logic/Theory Examples
To get started, some simple examples are provided in *[simple_monosat_examples]* directory. It includes examples on graph theory solver, and logic solver (SAT) with/without hamming distance on BitVector solver, to show how SMT solver works in the SMT tool.


### Usages

Before running any algorithm provided in the package, either defenses or attacks, the usage print provides good information. The following is the usage provided in SMT tool, in which, the algorithms, examples, syntaxes, and hows to run are provided. 
```
  ____  __  __ _____      _   _   _             _
 / ___||  \/  |_   _|    / \ | |_| |_ __ _  ___| | __
 \___ \| |\/| | | |     / _ \| __| __/ _` |/ __| |/ /
  ___) | |  | | | |    / ___ \ |_| || (_| | (__|   < 
 |____/|_|  |_| |_|   / _____ \__|\__\__,_|\___|_|\_\
      by GATE Lab, George Mason University

usage: SMT Tool, v 0.2.1
---------------------------------------------
                 smt_tool.py
---------------------------------------------
It is compatible with Python >= 3.0. Please use python3 for running this script.
---------------------------------------------
-h or --help:               Print This Message.
--algorithm (required):     It determines the algorithm selected to be run.
                            ------------- unlocking --------------- 
                                --reduced_sat                        
                                --eager_smt_dll                        
                                --lazy_smt_dll                        
                                --smt_approximate                        
                                --smt_hamming                        
                                --limited_sat                        
                                --limited_hamming                        
                            -------------- locking ----------------   
                                --random_enc                                           
                                --sarlock_enc                                            
--original:             Path to the original netlist as the input.
                            For unlocking: the original design (oracle) for logic simulation.
                            For locking: the original design targeted for locking.
--obfuscated:           Path to the obfuscated netlist.
                            For unlocking: the obfuscated design targeted for de-locking (decryption).
                            For locking: obfuscated file output address for locking.
--design_name           Design Name used for building temporary files/folders.
--key_str               Key string that would be used for SARLock
--rnd_percent           Percentage of Obfuscation in random logic locking
--tag                   Tag used for building temporary files/folders.
--verbose:              Verbosity Level. Can be 0, 1, 2, 3.
                            3 Debug Level,
                            2 Info Level,
                            1 Warning Level,
                            0 Error Level.
                            Default= "1" (Warning Level)
---------------------------------------------

SMT Attack Implementation with MonoSAT

optional arguments:
  -h, --help            show this help message and exit
  --algorithm ALGORITHM
                        The selected algorithm (defense or attack)
  --original ORIGINAL   original benchmark path
  --obfuscated OBFUSCATED
                        obfuscated benchmark path
  --combined_dll COMBINED_DLL
                        not used currently
  --design_name DESIGN_NAME
                        top module name
  --iteration ITERATION
                        iteration for limited run
  --tag TAG             current run tag
  --verbose VERBOSE     verbosity level


```









[MonoSAT]: https://github.com/sambayless/monosat
[monotonic theories]: http://www.cs.ubc.ca/labs/isd/Projects/monosat/smmt.pdf
[simple_monosat_examples]: https://github.com/hmkamali/smt/tree/master/simple_monosat_examples





