import cirq
from qramcircuits.toffoli_decomposition import ToffoliDecompType

import qramcircuits.bucket_brigade as bb

import optimizers as qopt

import time

import os
import psutil
import sys


def main(argv_param, nr):

    # print("Hello QRAM circuit experiments!", argv_param, nr)

    if argv_param == "decomp":
        """
            Bucket brigade - DECOMP
        """
        decomp_scenario = bb.BucketBrigadeDecompType(
            [
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4_COMPUTE,
                # fan_in_decomp
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4,  # mem_decomp
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE,
                # fan_out_decomp
            ],
            False
        )
    else:
        """
           Bucket brigade - NO DECOMP
        """
        decomp_scenario = bb.BucketBrigadeDecompType(
            [
                ToffoliDecompType.NO_DECOMP,  # fan_in_decomp
                ToffoliDecompType.NO_DECOMP,  # mem_decomp
                ToffoliDecompType.NO_DECOMP,  # fan_out_decomp
            ],
            False
        )

    for i in range(nr, nr + 1):

        nr_qubits = i
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))


        start = time.time()
        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=decomp_scenario)
        # print(bbcircuit.circuit.to_text_diagram(use_unicode_characters=False,
        #                                         qubit_order = bbcircuit.qubit_order))
        stop = time.time() - start

        process = psutil.Process(os.getpid())
        """
        rss: aka “Resident Set Size”, this is the non-swapped physical memory a 
        process has used. On UNIX it matches “top“‘s RES column). 
        vms: aka “Virtual Memory Size”, this is the total amount of virtual 
        memory used by the process. On UNIX it matches “top“‘s VIRT column. 
        """

        print("--> mem bucket brigade, ", argv_param, ",", nr_qubits,
              ",", stop,
              ",", process.memory_info().rss ,
              ",", process.memory_info().vms , flush=True)

if __name__ == "__main__":

    # If param is decomp - decomposition
    # Otherwise no_decomp
    if len(sys.argv) == 1:
        print("If param is decomp runs experiment with decomposition. "
              "Any other string no decomposition.")
    else:
        main(sys.argv[1], int(sys.argv[2]))


