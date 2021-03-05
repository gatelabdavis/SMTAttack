#Import the MonoSAT library
from monosat import *

import methods_lock
import math
from random import *
import argparse
import logging

import sys


def sarlock_enc(args):

    logging.error("************************ Starting dll_replace **********************")

    rnd_obf_bench_address = args.original     # sys.argv[1] > original bench name
    sar_rnd_obf_bench_address = args.obfuscated
    key_str = args.key_str

    bench_file = open(rnd_obf_bench_address)
    rnd_key_cnt = 0

    inp_list = []

    xor_gates = ""
    flip_sig = ""
    mask_sig = ""
    not_key_list = ""
    new_keys_str = ""

    old_keys_str = ""
    output_str = ""
    input_str = ""
    gates_str = ""

    selected_output = ""


    for line in bench_file:
        if "INPUT(keyinput" in line:
            rnd_key_cnt += 1
            old_keys_str += line
        elif "INPUT" in line:
            inp_list.append(line[line.find("(") + 1:line.find(")")])
            input_str += line
        elif "OUTPUT" in line:
            selected_output = line[line.find("(") + 1:line.find(")")]
            output_str += line
        elif " = " in line:
            gates_str += line

    bench_file.close()

    for i in range(0, len(inp_list)):
        xor_gates += "nXoR" + str(i) + " = XOR(" + inp_list[i] + ", " + "keyinput" + str(i+rnd_key_cnt) + ")\n"
        new_keys_str += "INPUT(keyinput" + str(i+rnd_key_cnt) + ")\n"

    flip_sig_list = ""
    if len(inp_list) < 10:
        for i in range(0, len(inp_list)):
            if i == 0:
                flip_sig = "flipSig = NOR(nXoR" + str(i) + ", "
            elif i == len(inp_list) - 1:
                flip_sig += "nXoR" + str(i) + ")\n"
            else:
                flip_sig += "nXoR" + str(i) + ", "
    else:
        cnt_flip_list = int(len(inp_list)/10) + 1
        for i in range(0, int(len(inp_list)/10)):
            for j in range(0, 10):
                if j == 0:
                    flip_sig = "flipSig" + str(i) + " = OR(nXoR" + str(i*10 + j) + ", "
                elif j == 9:
                    flip_sig += "nXoR" + str(i*10 + j) + ")\n"
                else:
                    flip_sig += "nXoR" + str(i*10 + j) + ", "
            flip_sig_list += flip_sig
        for i in range(int(len(inp_list)/10)*10 + 1, len(inp_list)):
            if i == int(len(inp_list) / 10) * 10 + 1:
                flip_sig = "flipSig" + str(int(len(inp_list)/10)) + " = OR(nXoR" + str(i) + ", "
            elif i == len(inp_list) - 1:
                flip_sig += "nXoR" + str(i) + ")\n"
            else:
                flip_sig += "nXoR" + str(i) + ", "
        flip_sig_list += flip_sig

        for i in range(0, cnt_flip_list):
            if i == 0:
                flip_sig = "flipSig = NOR(flipSig" + str(i) + ", "
            elif i == cnt_flip_list - 1:
                flip_sig += "flipSig" + str(i) + ")\n"
            else:
                flip_sig += "flipSig" + str(i) + ", "

    for i in range(0, len(key_str)):
        not_key_list += "not_keyinp" + str(i+rnd_key_cnt) + " = NOT(keyinput" + str(i+rnd_key_cnt) + ")\n"

    mask_sig_list = ""
    if len(inp_list) < 10:
        for i in range(0, len(inp_list)):
            if i == 0:
                if key_str[i] == "0":
                    mask_sig = "maskSig = AND(not_keyinp" + str(i+rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig = "maskSig = AND(keyinput" + str(i + rnd_key_cnt) + ", "
            elif i == len(inp_list) - 1:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i+rnd_key_cnt) + ")\n"
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i+rnd_key_cnt) + ")\n"
            else:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i+rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i+rnd_key_cnt) + ", "
    else:
        cnt_mask_list = int(len(inp_list) / 10) + 1
        for i in range(0, int(len(inp_list) / 10)):
            for j in range(0, 10):
                if j == 0:
                    if key_str[j] == "0":
                        mask_sig = "maskSig" + str(i) + " = AND(not_keyinp" + str(i*10 + j + rnd_key_cnt) + ", "
                    elif key_str[i] == "1":
                        mask_sig = "maskSig" + str(i) + " = AND(keyinput" + str(i * 10 + j + rnd_key_cnt) + ", "
                elif j == 9:
                    if key_str[j] == "0":
                        mask_sig += "not_keyinp" + str(i*10 + j + rnd_key_cnt) + ")\n"
                    elif key_str[i] == "1":
                        mask_sig += "keyinput" + str(i*10 + j + rnd_key_cnt) + ")\n"
                else:
                    if key_str[i] == "0":
                        mask_sig += "not_keyinp" + str(i*10 + j + rnd_key_cnt) + ", "
                    elif key_str[i] == "1":
                        mask_sig += "keyinput" + str(i*10 + j + rnd_key_cnt) + ", "
            mask_sig_list += mask_sig

        for i in range(int(len(inp_list) / 10) * 10, len(inp_list)):
            if i == int(len(inp_list) / 10) * 10:
                if key_str[i] == "0":
                    mask_sig = "maskSig" + str(int(len(inp_list)/10)) + " = AND(not_keyinp" + str(i + rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig = "maskSig" + str(int(len(inp_list)/10)) + " = AND(keyinput" + str(i + rnd_key_cnt) + ", "
            elif i == len(inp_list) - 1:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i + rnd_key_cnt) + ")\n"
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i + rnd_key_cnt) + ")\n"
            else:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i + rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i + rnd_key_cnt) + ", "
        mask_sig_list += mask_sig

        for i in range(0, cnt_mask_list):
            if i == 0:
                mask_sig = "maskSig = AND(maskSig" + str(i) + ", "
            elif i == cnt_mask_list - 1:
                mask_sig += "maskSig" + str(i) + ")\n"
            else:
                mask_sig += "maskSig" + str(i) + ", "

    not_mask = "not_mask = NOT(maskSig)\n"
    mask_flip = "flip_mask = AND(flipSig, not_mask)\n"

    new_bench = input_str + "\n" + old_keys_str + "\n" + new_keys_str + "\n" + output_str + "\n" + gates_str + "\n" + xor_gates + "\n" + not_key_list + "\n" + flip_sig_list + "\n" + flip_sig + "\n" + mask_sig_list + "\n" + mask_sig + "\n" + not_mask + "\n" + mask_flip + "\n"
    new_bench = new_bench.replace(selected_output + " = ", selected_output + "_enc = ")

    new_bench += selected_output + " = XOR(" + selected_output + "_enc, flip_mask)\n"

    bench_file = open(sar_rnd_obf_bench_address, "w")
    bench_file.write(new_bench)
    bench_file.close()

    logging.error("Written to {}.".format(args.obfuscated))


def rnd_enc(args):

    logging.error("************************ Starting dll_replace **********************")

    org_bench_address = args.original     # sys.argv[1] > original bench name
    if float(args.rnd_percent) < 0.1:
        percentage = "0" + str(int(float(args.rnd_percent) * 100))
    else:
        percentage = str(int(float(args.rnd_percent) * 100))

    rnd_obf_bench_folder = args.obfuscated          # sys.argv[2] > tdb counts

    inserted = 0

    bench_gates = 0
    new_bench = ""

    bench_file = open(org_bench_address)
    for line in bench_file:
        new_bench += line
        if " = " in line:
            bench_gates += 1
    bench_file.close()

    randins_number = math.floor(float(args.rnd_percent) * bench_gates)

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

    logging.error("Written to {}.".format(rnd_obf_bench_folder))











