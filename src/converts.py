#Import the MonoSAT library
from monosat import *
import logicwire
import baseutils
import time
import copy
import operator
from random import randint

LOGIC_VALUE_ZERO = "0"
LOGIC_VALUE_ONE = "1"

PRIMARY_INPUT = "pin"
PRIMARY_OUTPUT = "pout"
KEY_INPUT = "kin"
INTERMEDIATE_WIRE = "inwire"

ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0


def int2bin(value, size):
    string_val = list("0" * size)
    temp_value = list(reversed(list("{0:b}".format(value))))
    for i in range(0, len(temp_value)):
        string_val[i] = temp_value[i]
    string_val = "".join(list(reversed(string_val)))
    return string_val


def bin2int(value):
    return int(value, 2)


def extract_logic(benchmark_address):

    new_bench = ""
    delay_key_list = []

    bench_file = open(benchmark_address)
    for line in bench_file:
        if "DELAY" in line:
            delay_oprs = line.split(", ")
            for i in range(0, len(delay_oprs)):
                if "keyinput" in delay_oprs[i]:
                    delay_key_list.append(delay_oprs[i])

    bench_file.close()

    bench_file = open(benchmark_address)

    for line in bench_file:
        if "INPUT" in line:
            if line[line.find("(") + 1 : line.find(")")] not in delay_key_list:
                new_bench += line
            else:
                new_bench += "\n"
        elif "_old = " in line:
            line = line.replace("_old", "")
            new_bench += line
        elif "DELAY" in line:
            new_bench += "\n"
        else:
            new_bench += line

    bench_file.close()

    bench_file_name = benchmark_address[benchmark_address.find("dll_obfuscated/") + 15: benchmark_address.find(".bench")]
    bench_folder = benchmark_address[0: benchmark_address.find("dll_obfuscated/")]

    extracted_bench_address = bench_folder + "logic_extracted/" + bench_file_name + ".bench"

    new_bench_file = open(extracted_bench_address, 'w')
    new_bench_file.write(new_bench)
    new_bench_file.close()


def delaybench2muxbench(benchmark_address):

    bench_file = open(benchmark_address)

    new_bench = ""

    for line in bench_file:
        if "DELAY" in line:
            delay_list_inputs = line[line.find("(") + 1:line.find(")")]
            delay_oprs = delay_list_inputs.split(", ")
            gate_out = line[0: line.find(" =")]
            new_bench += gate_out + " = MUX(" + delay_oprs[3] + ", " + delay_oprs[0] + ", " + delay_oprs[0] + ")\n"
        else:
            new_bench += line

    bench_file.close()

    bench_file_name = benchmark_address[
                      benchmark_address.find("dll_obfuscated/") + 15: benchmark_address.find(".bench")]
    bench_folder = benchmark_address[0: benchmark_address.find("dll_obfuscated/")]

    extracted_bench_address = bench_folder + "dll_muxed/" + bench_file_name + ".bench"

    new_bench_file = open(extracted_bench_address, 'w')
    new_bench_file.write(new_bench)
    new_bench_file.close()



def circuit2bool(interwires, poutwires, pin, keyin): #wires are inwire + pout

    interwires_var = [None] * (len(interwires))
    poutwires_var = [None] * (len(poutwires))

    baseutils.h_print(DBG_PR, "converts/circuit2bool: size of interwires:", len(interwires))
    baseutils.h_print(DBG_PR, "converts/circuit2bool: size of poutwires:", len(poutwires))

    baseutils.h_print(DBG_PR, "**********convert inter wires****************")
    for i in range(0, len(interwires)):
        operands_list = []

        baseutils.h_print(DBG_PR, "----------------------------------")
        baseutils.h_print(DBG_PR, "converts/circuit2bool: wire ", interwires[i].name, " = ", interwires[i].type)
        for j in range(0, len(interwires[i].operands)):
            if j != len(interwires[i].operands) - 1:
                baseutils.h_print(DBG_PR, interwires[i].operands[j].name, ", "),
            else:
                baseutils.h_print(DBG_PR, interwires[i].operands[j].name)
        baseutils.h_print(DBG_PR, ") ")

        baseutils.h_print(DBG_PR, " index = ", i, ", catg = ", interwires[i].catg)

        if interwires[i].type == "NOT" or interwires[i].type == "not":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[0].name, ": a ",
                  interwires[i].operands[0].catg)
            if interwires[i].operands[0].catg == PRIMARY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(pin[interwires[i].operands[0].index])
            elif interwires[i].operands[0].catg == KEY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(keyin[interwires[i].operands[0].index])
            elif interwires[i].operands[0].catg == INTERMEDIATE_WIRE:
                baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(interwires_var[interwires[i].operands[0].index])
            elif interwires[i].operands[0].catg == PRIMARY_OUTPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(poutwires_var[interwires[i].operands[0].index])

        elif interwires[i].type == "BUFF" or interwires[i].type == "buff" or interwires[i].type == "BUF" or interwires[i].type == "buf":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[0].name, ": a ",
                  interwires[i].operands[0].catg)
            if interwires[i].operands[0].catg == PRIMARY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(Not(pin[interwires[i].operands[0].index]))
            elif interwires[i].operands[0].catg == KEY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(Not(keyin[interwires[i].operands[0].index]))
            elif interwires[i].operands[0].catg == INTERMEDIATE_WIRE:
                baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(Not(interwires_var[interwires[i].operands[0].index]))
            elif interwires[i].operands[0].catg == PRIMARY_OUTPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[0].index, "]")
                interwires_var[i] = Not(Not(poutwires_var[interwires[i].operands[0].index]))

        elif interwires[i].type == "AND" or interwires[i].type == "and":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = And(operands_list)

        elif interwires[i].type == "NAND" or interwires[i].type == "nand":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Nand(operands_list)

        elif interwires[i].type == "OR" or interwires[i].type == "or":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Or(operands_list)

        elif interwires[i].type == "NOR" or interwires[i].type == "nor":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Nor(operands_list)

        elif interwires[i].type == "XOR" or interwires[i].type == "xor":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Xor(operands_list)

        elif interwires[i].type == "XNOR" or interwires[i].type == "xnor":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Xnor(operands_list)
        elif interwires[i].type == "MUX" or interwires[i].type == "mux":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(interwires[i].operands), " operands!")
            for j in range(0, len(interwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", interwires[i].operands[j].name, ": a ",
                      interwires[i].operands[j].catg)
                if interwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", interwires[i].operands[j].index, "]")
                    operands_list.append(pin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", interwires[i].operands[j].index, "]")
                    operands_list.append(keyin[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", interwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[interwires[i].operands[j].index])
                elif interwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            interwires_var[i] = Or(And(Not(operands_list[0]), operands_list[1]), And(operands_list[0], operands_list[2]))

        interwires_var[i].symbol = interwires[i].name

        baseutils.h_print(DBG_PR, "**********convert out wires****************")
    for i in range(0, len(poutwires)):
        operands_list = []

        baseutils.h_print(DBG_PR, "----------------------------------")
        baseutils.h_print(DBG_PR, "converts/circuit2bool: wire", poutwires[i].name, " = ", poutwires[i].type, "(")
        for j in range(0, len(poutwires[i].operands)):
            if j != len(poutwires[i].operands) - 1:
                baseutils.h_print(DBG_PR, poutwires[i].operands[j].name, ", "),
            else:
                baseutils.h_print(DBG_PR, poutwires[i].operands[j].name)
                baseutils.h_print(DBG_PR, ") ")

        baseutils.h_print(DBG_PR, "index = ", i, ", catg = ", poutwires[i].catg)

        if poutwires[i].type == "NOT" or poutwires[i].type == "not":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(poutwires[i].operands), " operands!")
            baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[0].name, ": a ",
                  poutwires[i].operands[0].catg)
            if poutwires[i].operands[0].catg == PRIMARY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(pin[poutwires[i].operands[0].index])
            elif poutwires[i].operands[0].catg == KEY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(keyin[poutwires[i].operands[0].index])
            elif poutwires[i].operands[0].catg == INTERMEDIATE_WIRE:
                baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(interwires_var[poutwires[i].operands[0].index])
            elif poutwires[i].operands[0].catg == PRIMARY_OUTPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PO[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(poutwires_var[poutwires[i].operands[0].index])

        elif poutwires[i].type == "BUFF" or poutwires[i].type == "buff" or poutwires[i].type == "BUF" or poutwires[i].type == "buf":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(poutwires[i].operands), " operands!")
            baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[0].name, ": a ",
                  poutwires[i].operands[0].catg)
            if poutwires[i].operands[0].catg == PRIMARY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(Not(pin[poutwires[i].operands[0].index]))
            elif poutwires[i].operands[0].catg == KEY_INPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(Not(keyin[poutwires[i].operands[0].index]))
            elif poutwires[i].operands[0].catg == INTERMEDIATE_WIRE:
                baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(Not(interwires_var[poutwires[i].operands[0].index]))
            elif poutwires[i].operands[0].catg == PRIMARY_OUTPUT:
                baseutils.h_print(DBG_PR, " equal with = VAR_PO[", poutwires[i].operands[0].index, "]")
                poutwires_var[i] = Not(Not(poutwires_var[poutwires[i].operands[0].index]))

        elif poutwires[i].type == "AND" or poutwires[i].type == "and":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(poutwires[i].operands), " operands!")
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = And(operands_list)

        elif poutwires[i].type == "NAND" or poutwires[i].type == "nand":
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = Nand(operands_list)

        elif poutwires[i].type == "OR" or poutwires[i].type == "or":
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = Or(operands_list)

        elif poutwires[i].type == "NOR" or poutwires[i].type == "nor":
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = Nor(operands_list)

        elif poutwires[i].type == "XOR" or poutwires[i].type == "xor":
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = Xor(operands_list)

        elif poutwires[i].type == "XNOR" or poutwires[i].type == "xnor":
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                      poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", interwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[poutwires[i].operands[j].index])
            poutwires_var[i] = Xnor(operands_list)

        elif poutwires[i].type == "MUX" or poutwires[i].type == "mux":
            baseutils.h_print(DBG_PR, "converts/circuit2bool: has ", len(poutwires[i].operands), " operands!")
            for j in range(0, len(poutwires[i].operands)):
                baseutils.h_print(DBG_PR, "converts/circuit2bool: operand[", j, "] = ", poutwires[i].operands[j].name, ": a ",
                                  poutwires[i].operands[j].catg)
                if poutwires[i].operands[j].catg == PRIMARY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(pin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == KEY_INPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_KI[", poutwires[i].operands[j].index, "]")
                    operands_list.append(keyin[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == INTERMEDIATE_WIRE:
                    baseutils.h_print(DBG_PR, " equal with = VAR_II[", poutwires[i].operands[j].index, "]")
                    operands_list.append(interwires_var[poutwires[i].operands[j].index])
                elif poutwires[i].operands[j].catg == PRIMARY_OUTPUT:
                    baseutils.h_print(DBG_PR, " equal with = VAR_PO[", poutwires[i].operands[j].index, "]")
                    operands_list.append(poutwires_var[interwires[i].operands[j].index])
            poutwires_var[i] = Or(And(Not(operands_list[0]), operands_list[1]), And(operands_list[0], operands_list[2]))

        poutwires_var[i].symbol = poutwires[i].name

    return poutwires_var



