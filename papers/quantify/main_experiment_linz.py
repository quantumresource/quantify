import cirq
from qramcircuits.toffoli_decomposition import ToffoliDecompType

import qramcircuits.bucket_brigade as bb

import optimizers as qopt

import time


def main():

    print("Hello QRAM circuit experiments!")
    

    for i in range(2, 16):

        nr_qubits = i
        qubits = []
        for i in range(nr_qubits):
            qubits.append(cirq.NamedQubit("a" + str(i)))

        """
            Bucket brigade
        """

        decomp_scenario = bb.BucketBrigadeDecompType(
            [
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4_COMPUTE,    # fan_in_decomp
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_4,  # mem_decomp
                ToffoliDecompType.ZERO_ANCILLA_TDEPTH_0_UNCOMPUTE,    # fan_out_decomp
            ],
            False
        )

        # Simulation without parallelisation optimisation
        start1 = time.time()
        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario = decomp_scenario)
        stop1 = time.time() - start1


        # Simulation with parallelisation optimisation
        decomp_scenario.parallel_toffolis = True
        start2 = time.time()
        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=decomp_scenario)
        stop2 = time.time() - start2

        # #Verification
        bbcircuit.verify_number_qubits()
        bbcircuit.verify_depth(
            Alexandru_scenario=decomp_scenario.parallel_toffolis)

        bbcircuit.verify_T_count()
        bbcircuit.verify_T_depth(
            Alexandru_scenario=decomp_scenario.parallel_toffolis)
        bbcircuit.verify_hadamard_count(
            Alexandru_scenario=decomp_scenario.parallel_toffolis)
        bbcircuit.verify_cnot_count(
            Alexandru_scenario=decomp_scenario.parallel_toffolis)

        end = time.time()
        print("--> exp bucket brigade, ", nr_qubits, ",", stop1 , ",", stop2, ",", flush=True)


if __name__ == "__main__":

    # import cProfile
    # cProfile.run("main()")
    main()


