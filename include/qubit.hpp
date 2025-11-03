#ifndef QUBIT_HPP
#define QUBIT_HPP

#include <vector>
#include <algorithm>


class Qubit {
    int qubit_id;
    int T_count;

    //to replace with heap
    std::vector<int> CNOT_count;

public:

    Qubit(int id, int t_count, const std::vector<int>& cnot_counts) : qubit_id(id), T_count(t_count), CNOT_count(cnot_counts) {}

    //to replace with heap
    int max_cnot_count() const {
        int max_count = 0;
        for (int count : CNOT_count) {
            if (count > max_count) {
                max_count = count;
            }
        }
        return max_count;
    }

    bool operator ==(const Qubit& other) const {
        return qubit_id == other.qubit_id &&
               T_count == other.T_count &&
               CNOT_count == other.CNOT_count;
    }

    int const getTCount() const {
        return T_count;
    }

    int const getCNOTCount(int other_qubit_index) const {
        return CNOT_count[other_qubit_index];
    }

    int const getQubitID() const {
        return qubit_id;
    }

    void incrementTCount() {
        T_count++;
    }

    void incrementCNOTCount(int other_qubit_index) {
        CNOT_count[other_qubit_index]++;
    }
};

#endif // QUBIT_HPP