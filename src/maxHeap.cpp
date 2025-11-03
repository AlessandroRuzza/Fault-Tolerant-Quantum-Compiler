#include "maxHeap.hpp"
#include "circuit.hpp"

// Esplicite istanziazioni: le implementazioni sono in include/maxHeap.tpp

template <>
int MaxHeap<int*>::heapify_metric(int index) const
{
    return *array[index];
}

template <>
int MaxHeap<Qubit*>::heapify_metric(int index) const
{
    return array[index]->getTCount() + array[index]->max_cnot_count();
}
