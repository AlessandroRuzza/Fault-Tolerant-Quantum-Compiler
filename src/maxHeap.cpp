#include "maxHeap.hpp"
#include "circuit.hpp"

// template class MaxHeap<int>;
// template class MaxHeap<circuit::Qubit>;

template <>
int MaxHeap<int>::heapify_metric(int index) const {
    return array[index];
}

template <>
int MaxHeap<circuit::Qubit>::heapify_metric(int index) const {
    return array[index].T_count + array[index].max_cnot_count();
}

