import cirq
import mathematics
from optimizers import LookAheadAnalysis
from optimizers import MarkovAnalysis
from qramcircuits.toffoli_decomposition import ToffoliDecomposition, ToffoliDecompType


def main():

    adder_moments = mathematics.CarryRipple4TAdder(nr_qubits=16,
                                                     use_dual_ancilla=False).circuit.moments

    circuit = cirq.Circuit(ToffoliDecomposition.construct_decomposed_moments(adder_moments,
                                                                             ToffoliDecompType.ZERO_ANCILLA_TDEPTH_3))
    print(circuit)

    look_ahead_window = 3
    lookahead = LookAheadAnalysis(circuit)
    data_look = lookahead.lookahead(look_ahead_window,
                                    lookahead.find_T_gates,
                                    )
    markov = MarkovAnalysis(data_look)
    res_fukuda = markov.result_fukuda
    print(res_fukuda)
    print(markov.analysis_result.state_prob)

    """
        For verification purposes
    """
    sum = 0
    for x in res_fukuda:
        sum += x

    print("Sum", sum)
    print("Avg", markov.weighted_average(res_fukuda))
    print("Utl", markov.average_utilisation(res_fukuda))

    lookahead.plot_data(data_look)


if __name__ == "__main__":
    main()

