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

        # #
        # #
        # # #Create the search
        # #
        search = [0, 1, 2, 3]
        # search = list(range(0, 15))
        #

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
        # print(bbcircuit.circuit.to_text_diagram(use_unicode_characters=False,
        #                                         qubit_order = bbcircuit.qubit_order))


        # Simulation with parallelisation optimisation
        decomp_scenario.parallel_toffolis = True
        start2 = time.time()
        bbcircuit = bb.BucketBrigade(qubits,
                                     decomp_scenario=decomp_scenario)
        stop2 = time.time() - start2
        # print(bbcircuit.circuit.to_text_diagram(use_unicode_characters=False,
        #                                         qubit_order = bbcircuit.qubit_order))




        # print(bbcircuit.circuit.to_text_diagram(use_unicode_characters=False,
        #                                         qubit_order = bbcircuit.qubit_order))

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

    # qopt.CommuteTGatesToStart().optimize_circuit(bbcircuit.circuit)
    #
    # print(bbcircuit.circuit)

    # qopt.SearchCNOTPattern().optimize_circuit(bbcircuit.circuit)

    # qopt.CancelNghCNOTs().apply_until_nothing_changes(bbcircuit.circuit,
    #                                                   cu.count_cnot_of_circuit)
    # print(bbcircuit.circuit)
    # print("*** Large Depth Small Width:")
    # """
    # be sure while testing that the number of search values are a power of 2
    # and that the binary decomposition of each search value is less or equal to the number of qubits' address
    # like if we have 4 qubits then the search values should range between 0 and 15
    # """
    # ldsmcircuit = ldsw.LargeDepthSmallWidth(qubits,
    #                                         search,
    #                                         decomp_type = MPMCTDecompType.ALLOW_DECOMP)
    # print((ldsmcircuit.circuit))
    # print("Verify N_q:      {}\n".format(ldsmcircuit.verify_number_qubits()))
    # print("Verify D:        {}\n".format(ldsmcircuit.verify_depth()))
    # print("Verify T_c:      {}\n".format(ldsmcircuit.verify_T_count()))
    # print("Verify T_d:      {}\n".format(ldsmcircuit.verify_T_depth()))
    # print("Verify H_c:      {}\n".format(ldsmcircuit.verify_hadamard_count()))
    # print("Verify CNOT_c:   {}\n".format(ldsmcircuit.verify_cnot_count()))
    # #
    # qopt.CommuteTGatesToStart().optimize_circuit(ldsmcircuit.circuit)

    # print("*** Small Depth Large Width:")
    # #be sure while testing that the number of search values are a power of 2
    # #and that the binary decomposition of each search value is less or equal to the number of qubits' address
    # # like if we have 4 qubits then the search values should range between 0 and 15
    # sdlwcircuit = sdlw.SmallDepthLargeWidth(qubits,
    #                                         search,
    #                                         decomp_type = MPMCTDecompType.ALLOW_DECOMP)
    # print(sdlwcircuit.circuit)
    # print("Verify N_q:      {}\n".format(sdlwcircuit.verify_number_qubits()))
    # print("Verify D:        {}\n".format(sdlwcircuit.verify_depth()))  #still working on the depth
    # print("Verify T_d:      {}\n".format(sdlwcircuit.verify_T_depth()))
    # print("Verify T_c:      {}\n".format(sdlwcircuit.verify_T_count()))
    # print("Verify H_c:      {}\n".format(sdlwcircuit.verify_hadamard_count()))
    # print("Verify CNOT_c:   {}\n".format(sdlwcircuit.verify_cnot_count()))


if __name__ == "__main__":

    # import cProfile
    # cProfile.run("main()")
    main()


