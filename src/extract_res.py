import baseutils

ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

if __name__ == "__main__":

    baseutils.h_print(WAR_PR, "************************ Starting Main **********************")

    reports_directory = "../benchmarks/reports/"

    num_reports = 60
    bench_name = "c432"

    iter = ""
    func_time = ""
    nonfunc_time = ""

    csv_content = ""

    for i in range(1, num_reports):
        bench_file = open(reports_directory + bench_name + "_" + str(i) + ".txt")
        for line in bench_file:
            if "func_iteration" in line:
                iter = line[line.find("func_iteration=") + 16 : line.find(";")]
                func_time = line[line.find("func_exe_time=") + 15 : line.find("; non")]
                nonfunc_time = line[line.find("nonfunc_exe_time=") + 18 : line.find("nonfunc_exe_time=") + 28]
        csv_content += str(i) + ", " + iter + ", " + func_time + ", " + nonfunc_time + "\n"
        bench_file.close()

    write_file = open(reports_directory + bench_name + "_reports.csv", "w")
    write_file.write(csv_content)
    write_file.close()

