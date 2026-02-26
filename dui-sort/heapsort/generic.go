package heapsort

import (
	"sort"
)

// Heap is a generic heap that implements sort.Interface for heap sort.
// It uses a custom comparison function to support any type that can be compared.
type Heap[T any] struct {
	data []T
	less func(a, b T) bool
}

// NewHeap creates a new Heap from a slice and a less function.
// The less function should return true if a < b.
func NewHeap[T any](data []T, less func(a, b T) bool) *Heap[T] {
	return &Heap[T]{
		data: data,
		less: less,
	}
}

// Len implements sort.Interface.
func (h *Heap[T]) Len() int {
	return len(h.data)
}

// Less implements sort.Interface.
// It uses the custom less function to compare elements.
func (h *Heap[T]) Less(i, j int) bool {
	return h.less(h.data[i], h.data[j])
}

// Swap implements sort.Interface.
func (h *Heap[T]) Swap(i, j int) {
	h.data[i], h.data[j] = h.data[j], h.data[i]
}

// Heapify builds a max heap from the heap's data.
func (h *Heap[T]) Heapify() {
	// Start from the last non-leaf node and sift down each node
	// Last non-leaf node is at index (len(data) / 2) - 1
	for i := h.Len()/2 - 1; i >= 0; i-- {
		h.siftDown(i, h.Len())
	}
}

// SiftDown maintains the max heap property by sifting down
// the element at index 'root' down to its proper position.
// 'heapSize' is the size of the heap to consider.
func (h *Heap[T]) siftDown(root, heapSize int) {
	for {
		largest := root
		left := 2*root + 1
		right := 2*root + 2

		// Check if left child exists and is greater than current largest
		if left < heapSize && h.Less(largest, left) {
			largest = left
		}

		// Check if right child exists and is greater than current largest
		if right < heapSize && h.Less(largest, right) {
			largest = right
		}

		// If largest is still root, we're done
		if largest == root {
			break
		}

		// Swap root with the largest child
		h.Swap(root, largest)

		// Continue sifting down from the child position
		root = largest
	}
}

// Sort sorts the heap data in place using heap sort algorithm.
// After sorting, the data will be in ascending order according to the less function.
func (h *Heap[T]) Sort() {
	if h.Len() <= 1 {
		return
	}

	// Build max heap
	h.Heapify()

	// Extract elements from heap one by one
	for i := h.Len() - 1; i > 0; i-- {
		// Swap root (maximum) with the last element
		h.Swap(0, i)

		// Restore heap property for the reduced heap
		h.siftDown(0, i)
	}
}

// GenericHeapSort sorts a slice using the heap sort algorithm with a custom less function.
// It modifies the slice in place and returns it.
// The less function should return true if a < b.
func GenericHeapSort[T any](data []T, less func(a, b T) bool) {
	if len(data) <= 1 {
		return
	}

	h := NewHeap(data, less)
	h.Sort()
}

// HeapSortFunc provides a convenient function for sorting slices using heap sort.
// It takes a slice and a less function, and sorts the slice in place.
// The less function should return true if a < b.
func HeapSortFunc[T any](data []T, less func(a, b T) bool) {
	GenericHeapSort(data, less)
}

// Sorted returns a new sorted slice, leaving the original unchanged.
// The less function should return true if a < b.
func Sorted[T any](data []T, less func(a, b T) bool) []T {
	if len(data) <= 1 {
		return append([]T{}, data...)
	}

	result := make([]T, len(data))
	copy(result, data)

	GenericHeapSort(result, less)
	return result
}

// IntHeap is a type that implements sort.Interface for []int with ascending order.
type IntHeap []int

// Len implements sort.Interface.
func (h IntHeap) Len() int {
	return len(h)
}

// Less implements sort.Interface.
func (h IntHeap) Less(i, j int) bool {
	return h[i] < h[j]
}

// Swap implements sort.Interface.
func (h IntHeap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
}

// Push adds an element to the heap.
func (h *IntHeap) Push(x any) {
	*h = append(*h, x.(int))
}

// Pop removes and returns the largest element from the heap.
func (h *IntHeap) Pop() any {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// IntHeapSort sorts an IntHeap in place.
func IntHeapSort(h *IntHeap) {
	sort.Sort(h)
}

// ReverseIntHeap is a type that implements sort.Interface for []int with descending order.
type ReverseIntHeap []int

// Len implements sort.Interface.
func (h ReverseIntHeap) Len() int {
	return len(h)
}

// Less implements sort.Interface (reversed).
func (h ReverseIntHeap) Less(i, j int) bool {
	return h[i] > h[j]
}

// Swap implements sort.Interface.
func (h ReverseIntHeap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
}

// StringHeap is a type that implements sort.Interface for []string with ascending order.
type StringHeap []string

// Len implements sort.Interface.
func (h StringHeap) Len() int {
	return len(h)
}

// Less implements sort.Interface.
func (h StringHeap) Less(i, j int) bool {
	return h[i] < h[j]
}

// Swap implements sort.Interface.
func (h StringHeap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
}

// Float64Heap is a type that implements sort.Interface for []float64 with ascending order.
type Float64Heap []float64

// Len implements sort.Interface.
func (h Float64Heap) Len() int {
	return len(h)
}

// Less implements sort.Interface.
func (h Float64Heap) Less(i, j int) bool {
	return h[i] < h[j]
}

// Swap implements sort.Interface.
func (h Float64Heap) Swap(i, j int) {
	h[i], h[j] = h[j], h[i]
}
