#Import the MonoSAT library
from monosat import *

import methods_unlock
import baseutils

import methods_lock

import argparse
import logging

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0


def usage_print(name=None):
    return '''SMT Tool, v 0.2.1
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
--key_str               Key string that would be used for SARLock
--rnd_percent           Percentage of Obfuscation in random logic locking
--design_name           Design Name used for building temporary files/folders.
--tag                   Tag used for building temporary files/folders.
--verbose:              Verbosity Level. Can be 0, 1, 2, 3.
                            3 Debug Level,
                            2 Info Level,
                            1 Warning Level,
                            0 Error Level.
                            Default= "1" (Warning Level)
---------------------------------------------
'''


if __name__ == "__main__":

    logging.basicConfig(format="%(funcName)s")
    logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(message)s"))
    logging.warning(r'  ____  __  __ _____      _   _   _             _    ')
    logging.warning(r' / ___||  \/  |_   _|    / \ | |_| |_ __ _  ___| | __')
    logging.warning(r' \___ \| |\/| | | |     / _ \| __| __/ _` |/ __| |/ /')
    logging.warning(r'  ___) | |  | | | |    / ___ \ |_| || (_| | (__|   < ')
    logging.warning(r' |____/|_|  |_| |_|   / _____\\__|\__\__,_|\___|_|\_\\')
    logging.warning(r'      by GATE Lab, George Mason University')
    logging.warning(r'')
    logging.getLogger().handlers[0].setFormatter(
        logging.Formatter("[%(funcName)s %(levelname)s] %(message)s"))

    parser = argparse.ArgumentParser(description='SMT Attack Implementation with MonoSAT', usage=usage_print())
    parser.add_argument("--algorithm", action="store", required=True, type=str, default="lazy_smt", help="The selected algorithm (defense or attack)")
    parser.add_argument("--original", action="store", required=True, type=str, default=" ", help="original benchmark path")
    parser.add_argument("--obfuscated", action="store", required=True, type=str, default=" ", help="obfuscated benchmark path")
    parser.add_argument('--combined_dll', action="store", required=False, type=int, default=0, help="not used currently")
    parser.add_argument('--maximum_delay', action="store", required=False, type=int, default=10, help="Maximum Delay for a Combinational Cone")
    parser.add_argument('--minimum_delay', action="store", required=False, type=int, default=10, help="Minimum Delay for a Combinational Cone")
    parser.add_argument('--design_name', action="store", required=False, type=str, default="design", help="top module name")
    parser.add_argument('--iteration', action="store", required=False, type=int, default=0, help="iteration for limited run")
    parser.add_argument('--tag', action="store", required=False, type=str, default="run_0", help="current run tag")
    parser.add_argument('--rnd_percent', action="store", required=False, type=float, default=0.2, help="Percentage of Random Obfuscation")
    parser.add_argument('--key_str', action="store", required=False, type=str, default="0", help="Key used for SARLock")
    parser.add_argument("--verbose", action="store", required=False, type=int, default=0, help="verbosity level")

    args = parser.parse_args()

    # logging.basicConfig(format="%(asctime)s %(levelname)s:: %(message)s", datefmt="%H:%M:%S")
    # logging.getLogger().handlers[0].setFormatter(logging.Formatter("%(message)s"))
    # logging.getLogger().handlers[0].setFormatter(
    #     logging.Formatter("[%(asctime)s.%(msecs)04d %(funcName)s %(levelname)s] %(message)s", datefmt="%H:%M:%S"))

    if int(args.verbose) == 0:
        logging.getLogger().setLevel(level=logging.ERROR)
    elif int(args.verbose) == 1:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif int(args.verbose) == 2:
        logging.getLogger().setLevel(level=logging.INFO)
    elif int(args.verbose) == 3:
        logging.getLogger().setLevel(level=logging.DEBUG)

    args_usage = parser.parse_args()

    if args.algorithm.lower() == "eager_smt_dll":  # dn
        methods_unlock.eager_dll_attack(args)
    elif args.algorithm.lower() == "reduced_sat":  # dn
        methods_unlock.reduced_sat_attack(args)
    elif args.algorithm.lower() == "smt_approximate":  # dn
        methods_unlock.smt_approximate_attack(args)
    elif args.algorithm.lower() == "lazy_smt_dll":  # dn
        methods_unlock.lazy_dll_attack(args)
    elif args.algorithm.lower() == "smt_hamming":  # dn
        methods_unlock.smt_hamming_sweep_attack(args)
    elif args.algorithm.lower() == "limited_sat":  # dn
        methods_unlock.limited_sat(args)
    elif args.algorithm.lower() == "limited_hamming":  # dn
        methods_unlock.limited_hamming(args)

    elif args.algorithm.lower() == "sarlock_enc":
        methods_lock.sarlock_enc(args)
    elif args.algorithm.lower() == "random_enc":
        methods_lock.rnd_enc(args)

    else:
        logging.error("The requested attack/defense algorithm is not defined in the SMT package.")











