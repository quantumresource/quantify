from mathematics.thaplyal1706 import QimMultiplier
from qramcircuits.toffoli_decomposition import *
from utils.counting_utils import *

import optimizers as qopt
import utils.misc_utils as miscutils

import time
import sys

def main():

      print(f"$$$ START {time.strftime('%H:%M:%S')}")

      for i in range(3, 8):
            print(f"2^{i} qubits")

            for j in range(10):
                  print(f"run {j}")

                  nr_bits = 2 ** i

                  A = [cirq.NamedQubit('A'+str(i)) for i in range(nr_bits)]
                  B = [cirq.NamedQubit('B'+str(i)) for i in range(nr_bits)]
                  # control = cirq.NamedQubit('ctrl')

                  multiplier = QimMultiplier(A, B).multiply()
                  # print(multiplier.moments)

                  decomp_mult = cirq.Circuit(ToffoliDecomposition.construct_decomposed_moments(multiplier.moments, ToffoliDecompType.FOUR_ANCILLA_TDEPTH_1_A))

                  # print("Before Optimization: ",
                  #       "depth:", len(decomp_mult),
                  #       "t-depth:", count_t_depth_of_circuit(decomp_mult),
                  #       "cnots:", count_cnot_of_circuit(decomp_mult),
                  #       "h:", count_h_of_circuit(decomp_mult),
                  #       "t-count:", count_t_of_circuit(decomp_mult))


                  start2 = time.time()

                  # miscutils.flag_operations(decomp_mult, [cirq.ops.H])
                  qopt.CancelNghHadamards(transfer_flag=False).optimize_circuit(decomp_mult)
                  qopt.CancelNghCNOTs(transfer_flag=False) \
                              .apply_until_nothing_changes(decomp_mult, count_cnot_of_circuit)


                  qopt.CommuteTGatesToStart().optimize_circuit(decomp_mult)
                  qopt.CommuteTGatesToStart().optimize_circuit(decomp_mult)
                  qopt.ParallelizeCNOTSToLeft().optimize_circuit(decomp_mult)

                  cirq.optimizers.DropEmptyMoments().optimize_circuit(decomp_mult)

                  stop2 = time.time() - start2
                  print(f"$$$ {time.strftime('%H:%M:%S')} stop: {stop2}")
                  sys.stdout.flush()

            # print(decomp_mult)

            # print("After Optimization:  ",
            #       "depth:", len(decomp_mult),
            #       "t-depth:", count_t_depth_of_circuit(decomp_mult),
            #       "cnots:", count_cnot_of_circuit(decomp_mult),
            #       "h:", count_h_of_circuit(decomp_mult),
            #       "t-count:", count_t_of_circuit(decomp_mult))

if __name__ == "__main__":
    main()
