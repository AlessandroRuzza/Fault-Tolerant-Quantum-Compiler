#ifndef MAXHEAP_HPP
#define MAXHEAP_HPP

#define DEFAULT_CAPACITY 10

// C++ Program for Implementing Max Heap
#include <iostream>
#include <vector>
#include <climits>
#include <functional>
#include <type_traits>
#include <stdexcept>


using namespace std;

// Template for MaxHeap
template <typename T>
// Class for MaxHeap
class MaxHeap {
private:
    std::vector<T> array;
    int size;
    int capacity;


public:
    // default ctor: non costruisce DEFAULT_CAPACITY elementi T (usa reserve)
    MaxHeap() : array(), size(0), capacity(0) {
        array.reserve(DEFAULT_CAPACITY);
    }

    // Constructor with capacity
    MaxHeap(int capacity)
        : array(), size(0), capacity(capacity){
        array.reserve(static_cast<size_t>(capacity));
    }

    // copy/move default
    MaxHeap(const MaxHeap&) = default;
    MaxHeap(MaxHeap&&) = default;
    MaxHeap& operator=(const MaxHeap&) = default;
    MaxHeap& operator=(MaxHeap&&) = default;

    // top overloads
    inline const T top() const {
        if (size <= 0) throw std::runtime_error("Heap is empty");
        return array[0];
    }
    inline T top() {
        if (size <= 0) throw std::runtime_error("Heap is empty");
        return array[0];
    }

    inline int getSize() const { return size; }
    inline bool isEmpty() const { return size == 0; }

    // getElementAt: const and non-const overloads (ritorna riferimento per poter modificare)
    inline const T getElementAt(int index) const {
        if (index < 0 || index >= size) throw std::out_of_range("Index out of range");
        return array[index];
    }

    inline T getElementAt(int index) {
        if (index < 0 || index >= size) throw std::out_of_range("Index out of range");
        return array[index];
    }
    
    // Function to heapify the node at index i
    void heapify(int i);

    // Function to build a max heap from a given array
    void buildHeap(const vector<T>& arr);

    // Function to insert a new value into the heap
    void insert(T value);

    // Function to remove and return the maximum value from the heap
    T pop();

    // Function to delete a specific key from the heap
    void deleteKey(T key);

    // Function to print the heap
    // void print() const;

    virtual int heapify_metric(int index) const;

};

#include "maxHeap.tpp"

#endif // MAXHEAP_HPP