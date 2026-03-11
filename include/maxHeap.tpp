#include "maxHeap.hpp"
#include <stdexcept>
#include <algorithm>

// Qubit definition used for specialized printing when T == Qubit*
#include "qubit.hpp"



template<typename T>
void MaxHeap<T>::buildHeap(const std::vector<T>& arr) {
    capacity = static_cast<int>(arr.size());
    size = capacity;
    array = arr;

    for (int i = (size - 1) / 2; i >= 0; --i) {
        heapify(i);
        if (i == 0) break; // evita loop infinito quando i è 0 e si decrementa oltre
    }
}


template<typename T>
T MaxHeap<T>::pop() {
    if (size <= 0)
        throw std::runtime_error("Heap is empty");
    if (size == 1) {
        size--;
        return array[0];
    }

    T root = array[0];
    array[0] = array[size - 1];
    size--;
    heapify(0);
    return root;
}

template<typename T>
void MaxHeap<T>::deleteKey(T key) {
    int index = -1;
    for (int i = 0; i < size; ++i) {
        if (array[i] == key) {
            index = i;
            break;
        }
    }
    if (index == -1) {
        return;
    }

    if (index == size - 1) {
        size--;
        return;
    }

    array[index] = array[size - 1];
    size--;
    heapify(index);
}

 
template<typename T>
void MaxHeap<T>::print() const {
    std::cout << "\nMax Heap: \n";
    for (int i = 0; i < size; ++i) {
        std::cout << *array[i] << std::endl;
    }
    std::cout << std::endl;
}

template<typename T>
void MaxHeap<T>::heapify(int i)
{
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < size && heapify_metric(left) > heapify_metric(largest))
        largest = left;

    if (right < size && heapify_metric(right) > heapify_metric(largest))
        largest = right;

    if (largest != i)
    {
        std::swap(array[i], array[largest]);
        heapify(largest);
    }
}

template<typename T>
void MaxHeap<T>::insert(T value)
{
    if (size == capacity)
    {
        capacity = (capacity == 0) ? 1 : capacity * 2;
        array.reserve(capacity);
    }

    int i = size;
    if (static_cast<int>(array.size()) == size) {
        array.push_back(value);
    } else {
        array[size] = value;
    }
    size++;

    while (i != 0 && heapify_metric((i - 1) / 2) < heapify_metric(i))
    {
        std::swap(array[i], array[(i - 1) / 2]);
        i = (i - 1) / 2;
    }
}
