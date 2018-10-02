#Import the MonoSAT library
import os
import baseutils
import copy
import time
import copy
import math
from random import *

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

if __name__ == "__main__":

    baseutils.h_print(WAR_PR, "************************ Starting rnd_replace **********************")

    org_bench_address = "../benchmarks/originals/" + sys.argv[1] + ".bench"     # sys.argv[1] > original bench name
    if float(sys.argv[2]) < 0.1:
        percentage = "0" + str(int(float(sys.argv[2]) * 100))
    else:
        percentage = str(int(float(sys.argv[2]) * 100))
    rnd_bname = sys.argv[1] + "_" + percentage + ".bench"
    rnd_obf_bench_folder = "../benchmarks/new_rnd/" + rnd_bname          # sys.argv[2] > tdb counts

    inserted = 0

    bench_gates = 0
    new_bench = ""

    bench_file = open(org_bench_address)
    for line in bench_file:
        new_bench += line
        if " = " in line:
            bench_gates += 1
    bench_file.close()

    randins_number = math.floor(float(sys.argv[2]) * bench_gates)

    bench_file = open(rnd_obf_bench_folder, "w")
    bench_file.write(new_bench)
    bench_file.close()

    while inserted < randins_number:
        new_gates = ""
        p_ins = ""
        p_outs = ""
        key_ins = ""
        bench_file = open(rnd_obf_bench_folder)
        for line in bench_file:
            if "INPUT(G" in line:
                p_ins += line
            elif "INPUT(key" in line:
                key_ins += line
            elif "OUTPUT" in line:
                p_outs += line
            elif " = " in line and "_old" not in line:
                if random() < randins_number/bench_gates and inserted < randins_number:
                    line1 = line.replace(" = ", "_enc = ")
                    gate_out = line[0: line.find(" =")]
                    if random() > 0.5:
                        line2 = gate_out + " = XNOR(keyinput" + str(inserted) + ", " + gate_out + "_enc)"
                        key_ins += "INPUT(keyinput" + str(inserted) + ")\n"
                    else:
                        line2 = gate_out + " = XOR(keyinput" + str(inserted) + ", " + gate_out + "_enc)"
                        key_ins += "INPUT(keyinput" + str(inserted) + ")\n"
                    new_gates += line1 + line2 + "\n"

                    inserted += 1

                else:
                    new_gates += line
            elif " = " in line and "_old" in line:
                new_gates += line

        bench_file.close()

        bench_file = open(rnd_obf_bench_folder, "w")
        bench_file.write(p_ins + "\n" + key_ins + "\n" + p_outs + "\n" + new_gates)
        bench_file.close()

    baseutils.h_print(ERR_PR, "written to ", rnd_obf_bench_folder)










