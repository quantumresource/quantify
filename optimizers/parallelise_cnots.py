import cirq

import utils.clifford_t_utils as ctu
import utils.counting_utils as count

from .invariant_check_optimizer import InvariantCheckOptimizer

class ParallelizeCNOTSToLeft(InvariantCheckOptimizer):

    def __init__(self):
        # Call the super constructor
        super().__init__(count.count_t_of_circuit)

    def optimization_at(self, circuit, index, op):

        # Search for normal CNOTs
        if not ctu.is_controlled_parallel_x(op):
            return None

        # print("start from 1", index, circuit[index], op)


        if op.gate == cirq.ops.CNOT:
            op = self.cnot_to_controlled_parallel_x(circuit, index, op)

        p_idx_control = index

        # Find the leftmost CNOT that shares the same control and
        # does not use the same target
        #   -> the prev moment is lower or none than the leftmost control moment

        prev_op = op
        # print("start from 2", p_idx_control, "-", circuit[p_idx_control], "-", prev_op)

        can_still_search_left = True
        while can_still_search_left:
            # The control wire
            tmp_idx_1 = circuit.prev_moment_operating_on([prev_op.qubits[0]],
                                                             p_idx_control)

            # The target wires
            tmp_idx_2 = -1
            for qub_idx, qub in enumerate(op.qubits[1:], 1):
                tmp_tmp = circuit.prev_moment_operating_on(
                    [ qub ],
                    p_idx_control)
                if tmp_tmp is None:
                    tmp_tmp = -1
                # print(" === ", qub, tmp_tmp, tmp_idx_2)
                # print(circuit[tmp_tmp])

                tmp_idx_2 = max(tmp_tmp, tmp_idx_2)

            # can_still_search_left = (tmp_idx_1 is not None) \
            #                         or (tmp_idx_2 is not None)
            #
            # if not can_still_search_left:
            #     break
            #
            # can_still_search_left = (tmp_idx_2 is None
            #                          and tmp_idx_1 is not None) \
            #                         or (tmp_idx_2 < tmp_idx_1)

            if tmp_idx_1 is None:
                tmp_idx_1 = -1

            if tmp_idx_2 is None:
                tmp_idx_2 = -1

            can_still_search_left = (tmp_idx_2 < tmp_idx_1)

            if not can_still_search_left:
                # print("cannot still search left", tmp_idx_1, tmp_idx_2)
                break

            potential_prev_op = circuit.operation_at(prev_op.qubits[0], tmp_idx_1)

            # Is this an operation we are searching for?
            can_still_search_left = can_still_search_left and \
                                    ctu.is_controlled_parallel_x(potential_prev_op)

            # # Does it share the control wire?
            # can_still_search_left = can_still_search_left and \
            #                         potential_prev_op.qubits[0] == op.qubits[0]

            # Does it share a control wire?
            can_still_search_left = can_still_search_left and \
                ctu.has_control_qubit(potential_prev_op, op.qubits[0])


            if can_still_search_left:
                prev_op = potential_prev_op
                p_idx_control = tmp_idx_1
                # print("  found", tmp_idx_1, tmp_idx_2, prev_op)


        # If nothing was found...do nothing
        if op == prev_op:
            return None

        current_controlled_op = prev_op
        if prev_op.gate == cirq.ops.CNOT:
            # This is a CNOT and not a more general Controlled Operation
            current_controlled_op = self.cnot_to_controlled_parallel_x(
                circuit, p_idx_control, prev_op
            )

        # Merge the old operation to the controlled Operation
        # nq = list(current_controlled_op.qubits) + [op.qubits[1]]
        # current_controlled_op = current_controlled_op.with_qubits(*nq)

        current_controlled_op = self.merge_controlled_parallel_x(op, current_controlled_op)

        self.update_operation(circuit,
                              p_idx_control,
                              prev_op,
                              current_controlled_op)

        # Remove the old operation
        circuit.clear_operations_touching(op.qubits, [ index ])

        # print(circuit)
        self.check_invariant(circuit)

        """
            Return None, in order to simplify the handling of gate insertion 
            and replacement... 
        """
        return None

    def update_operation(self, circuit, index, old_operation, new_operation):

        circuit.clear_operations_touching(old_operation.qubits, [index])
        circuit.insert(index, new_operation)


    def merge_controlled_parallel_x(self, op1, op2):

        if (len(op1.controls) != len(op2.controls)) \
            and (len(op1.controls) != 1) \
            and op1.controls[0] != op2.controls[0]:
                return

        merged_qubits = op1.sub_operation.qubits + \
                    op2.sub_operation.qubits

        try:
            p_op = cirq.ParallelGateOperation(cirq.ops.X,
                                              merged_qubits)
        except ValueError as e:
            print(e, merged_qubits)

        merged_op = cirq.ControlledOperation( [ op1.controls[0] ] ,
                                             sub_operation=p_op)

        return merged_op



    def cnot_to_controlled_parallel_x(self, circuit, index, operation):
        p_op = cirq.ParallelGateOperation(cirq.ops.X,
                                          [operation.qubits[1]])
        current_controlled_op = \
            cirq.ControlledOperation([operation.qubits[0]], p_op)

        # print("A--------> ", len(circuit))
        circuit.clear_operations_touching(operation.qubits, [index])
        # print("B--------> ", len(circuit), repr(circuit))

        # Is this an issue about how operations are inserted?
        circuit.insert(index + 1, current_controlled_op, strategy=cirq.InsertStrategy.INLINE)
        # print("C--------> ", len(circuit), repr(circuit))

        return current_controlled_op

"""
Experimental code
"""
# qubits = [cirq.NamedQubit("t" + str(i)) for i in range(5)]
# control = cirq.NamedQubit("control")
#
# sub_gate = cirq.ops.ParallelGateOperation(cirq.ops.X, qubits)
#
# cxxx = cirq.ops.ControlledOperation([control], sub_gate)
#
# circuit = cirq.Circuit(cxxx)
#
# print(circuit)