#Import the MonoSAT library
from monosat import *

import methods
import baseutils

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

if __name__ == "__main__":

    if sys.argv[1] == "dll_tck":
        methods.dll_tck()
    elif sys.argv[1] == "sat_tck":
        methods.sat_tck()
    elif sys.argv[1] == "ddip_tck":
        methods.ddip_tck()
    elif sys.argv[1] == "lazy_smt":
        methods.lazy_smt()
    elif sys.argv[1] == "minham_tck":
        methods.appsat_minham_tck()

    elif sys.argv[1] == "sat_cks":
        methods.sat_cks(int(sys.argv[2]))
    elif sys.argv[1] == "ham_cks":
        methods.ham_cks(int(sys.argv[2]))


    else:
        baseutils.h_print(ERR_PR, "tck option is not valid")












