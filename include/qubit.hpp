#ifndef QUBIT_HPP
#define QUBIT_HPP

#include <vector>
#include <algorithm>
#include <ostream>

class Qubit {
    int qubit_id;
    int T_count;

    //to replace with heap
    std::vector<int> CNOT_count;

//PERCHE QUI NON SERVE STD::TUPLE MENTRE IN GRAPH SI?????

//to replace with heap
private: 
    std::tuple<int, int> max_cnot_count() const {
    int c = 0;
    int max_count = 0;
    int index = -1;
    for (int count : CNOT_count) {
        if (count > max_count) {
            index = c;
            max_count = count;
        }
        c++;
    }
    return std::make_tuple(max_count, index);
}


public:

    Qubit(int id, int t_count, const std::vector<int>& cnot_counts) : qubit_id(id), T_count(t_count), CNOT_count(cnot_counts) {}

    //will call the top heap
    int getMaxCNOTCount() const {
        return get<0>(max_cnot_count());
    }

    int getMaxCNOTCountIndex() const {
        return get<1>(max_cnot_count());
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

// Stream output for Qubit - prints a compact summary without exposing internals.
inline std::ostream& operator<<(std::ostream& os, const Qubit& q) {
    return os << "Qubit{id=" << q.getQubitID()
              << ", T=" << q.getTCount()
              << ", CNOTmax=" << q.getMaxCNOTCount() << "}";
}

#endif // QUBIT_HPP