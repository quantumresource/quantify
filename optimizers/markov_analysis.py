import numpy as np
from utils import FukudaUtils


# from optimizers.lookahead_analysis import generate_csv_data
# import cirq

class AnalysisResult:
    def __init__(self, state_prob, max_state, total_transitions, trans_prob_matrix):
        self.state_prob, self.max_state, self.total_transitions, self.transition_probability_matrix\
            = state_prob, max_state, total_transitions, trans_prob_matrix


class MarkovAnalysis:

    def __init__(self, analysis_data):
        self.analysis_result = None
        self.result_fukuda = self.process_general_data(analysis_data)

    """"
        General procedure that processes general Markov chains
    """
    def process_general_data(self, look_ahead_table):
        current_state = 0

        # The states dictionary:
        # Each state is a key in the dictionary
        # the values are also stored in a dictionary where the keys in the ladder are
        # the arrival states transitioning from the state (key in the former) and the values
        # are the number of visites

        states_dict, total_transitions = {0: {}}, 0

        # Go through the analysis data
        for line in look_ahead_table:
            # Check the formatting of the file
            if len(line) != 3:
                # something is wrong
                # just continue
                print("This line is problem --", line)
                continue
            # update the number of transitions
            total_transitions += 1

            # Extract the next state
            next_state = int(line[1])

            # If this state was not encountered before then add it
            if next_state not in states_dict[current_state].keys():
                states_dict[current_state][next_state] = 0

            # Increase the counter of the current state
            states_dict[current_state][next_state] += 1

            # change the current state
            current_state = next_state

            # If the current state is not in the collection then introduce it
            if current_state not in states_dict:
                states_dict[current_state] = {}

        # Check that there is transition data to use
        assert (total_transitions > 0)

        # for checking that probabilities are correct
        check_transitions = 0

        states_prob = {}

        # We build the probabilities from the generated states' dictionary
        for state in states_dict:
            states_prob[state] = {}
            # For each state we determine the total number of times that it was visited
            # from all the other states
            sum_trans = sum(states_dict[state][key] for key in
                            states_dict[state].keys())
            for key in states_dict[state].keys():
                # The probabilities are then just the number of visit from a given state divided
                # by the total number of visits from all states
                states_prob[state][key] = states_dict[state][key] / sum_trans

            check_transitions += sum_trans

        assert (check_transitions == total_transitions)

        tran_prob_matrix = self.make_matrix(states_prob)

        self.analysis_result = AnalysisResult(states_prob, max(states_prob), total_transitions,
                                              tran_prob_matrix)
        print("Transition probabilities: {}" .format(self.analysis_result.state_prob))
        print("Total transitions: {} " .format(self.analysis_result.total_transitions))
        print("Maximum state: {}" .format(self.analysis_result.max_state))
        fh = FukudaUtils()
        res_fukuda = fh.markov(tran_prob_matrix)

        return res_fukuda


    def weighted_average(self, vector):
        avg = 0
        for i in range(len(vector)):
            avg += i * vector[i]
        return avg


    def average_utilisation(self, steady_vector):
        return 1 - steady_vector[0]


    def make_matrix(self, states_prob):
        """

        :param states_prob: dictionary of probability transition between states
        :return: probability transition matrix
        """
        size = max(states_prob) + 1
        matrix = np.zeros((size, size))
        for state in states_prob:
            for key in states_prob[state]:
                matrix[state][key] = states_prob[state][key]
        print(states_prob)
        return matrix

