#Import the MonoSAT library
import os
import baseutils
import copy
import time
import copy
import operator
from random import *

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

if __name__ == "__main__":

    baseutils.h_print(WAR_PR, "************************ Starting dll_replace **********************")

    org_bench_address = "../benchmarks/originals/" + sys.argv[1] + ".bench"     # sys.argv[1] > original bench name
    dll_bname = sys.argv[1] + "_dll_" + sys.argv[2] + ".bench"
    dll_obf_bench_folder = "../benchmarks/dll_obfuscated/" + dll_bname          # sys.argv[2] > tdb counts

    tdb_number = int(sys.argv[2])
    inserted = 0

    bench_gates = 0
    new_bench = ""

    bench_file = open(org_bench_address)
    for line in bench_file:
        new_bench += line
        if " = " in line:
            bench_gates += 1
    bench_file.close()

    bench_file = open(dll_obf_bench_folder, "w")
    bench_file.write(new_bench)
    bench_file.close()

    while inserted < tdb_number:
        new_gates = ""
        p_ins = ""
        p_outs = ""
        key_ins = ""
        bench_file = open(dll_obf_bench_folder)
        for line in bench_file:
            if "INPUT(G" in line:
                p_ins += line
            elif "INPUT(key" in line:
                key_ins += line
            elif "OUTPUT" in line:
                p_outs += line
            elif " = " in line and "_old" not in line:
                if random() < tdb_number/bench_gates and inserted < tdb_number:
                    line1 = line.replace(" = ", "_enc = ")
                    gate_out = line[0: line.find(" =")]
                    if random() > 0.5:
                        line2 = gate_out + "_old = XNOR(keyinput" + str(2*inserted) + ", " + gate_out + "_enc)"
                        key_ins += "INPUT(keyinput" + str(2*inserted) + ")\n"
                    else:
                        line2 = gate_out + "_old = XOR(keyinput" + str(2*inserted) + ", " + gate_out + "_enc)"
                        key_ins += "INPUT(keyinput" + str(2 * inserted) + ")\n"
                    if random() > 0.5:
                        if random() > 0.5:
                            line3 = gate_out + " = DELAY(" + gate_out + "_old, " + gate_out + "_1, " + gate_out + "_10, keyinput" + str(
                                2 * inserted + 1) + ", " + str(1) + ", " + str(50) + ")\n"
                            key_ins += "INPUT(keyinput" + str(2 * inserted + 1) + ")\n"
                        else:
                            line3 = gate_out + " = DELAY(" + gate_out + "_old, " + gate_out + "_1, " + gate_out + "_10, keyinput" + str(
                                2 * inserted + 1) + ", " + str(1) + ", " + str(50) + ")\n"
                            key_ins += "INPUT(keyinput" + str(2 * inserted + 1) + ")\n"
                    else:
                        if random() > 0.5:
                            line3 = gate_out + " = DELAY(" + gate_out + "_old, " + gate_out + "_1, " + gate_out + "_10, keyinput" + str(
                                2 * inserted + 1) + ", " + str(50) + ", " + str(1) + ")\n"
                            key_ins += "INPUT(keyinput" + str(2 * inserted + 1) + ")\n"
                        else:
                            line3 = gate_out + " = DELAY(" + gate_out + "_old, " + gate_out + "_1, " + gate_out + "_10, keyinput" + str(
                                2 * inserted + 1) + ", " + str(50) + ", " + str(1) + ")\n"
                            key_ins += "INPUT(keyinput" + str(2 * inserted + 1) + ")\n"
                    new_gates += line1 + line2 + "\n" + line3

                    inserted += 1

                else:
                    new_gates += line
            elif " = " in line and "_old" in line:
                new_gates += line

        bench_file.close()

        bench_file = open(dll_obf_bench_folder, "w")
        bench_file.write(p_ins + "\n" + key_ins + "\n" + p_outs + "\n" + new_gates)
        bench_file.close()

    baseutils.h_print(ERR_PR, "written to ", dll_obf_bench_folder)










