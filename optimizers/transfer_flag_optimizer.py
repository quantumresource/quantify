import cirq

class TransferFlagOptimizer(cirq.PointOptimizer):

    def __init__(self, transfer_flag = False):
        # Call the super constructor
        super().__init__()
        # should this operate only on flagged operations?
        self.transfer_flag = transfer_flag

    def apply_until_nothing_changes(self, circuit, criteria_to_int):
        count2 = -1
        n_count2 = -2
        while count2 != n_count2:
            count2 = n_count2
            self.optimize_circuit(circuit)
            n_count2 = criteria_to_int(circuit)
            # print("----", count2, n_count2)