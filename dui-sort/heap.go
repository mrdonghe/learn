package duisort

import "golang.org/x/exp/constraints"

// heapify maintains the max-heap property for the subtree rooted at index i.
// n is the size of the heap.
func heapify[T constraints.Ordered](arr []T, n, i int) {
	largest := i
	left := 2*i + 1
	right := 2*i + 2

	// Left child is larger than root
	if left < n && arr[left] > arr[largest] {
		largest = left
	}

	// Right child is larger than current largest
	if right < n && arr[right] > arr[largest] {
		largest = right
	}

	// If largest is not root, swap and continue heapifying
	if largest != i {
		arr[i], arr[largest] = arr[largest], arr[i]
		heapify(arr, n, largest)
	}
}

// BuildMaxHeap transforms an unsorted array into a max-heap.
// It starts from the last non-leaf node and goes up to the root.
func BuildMaxHeap[T constraints.Ordered](arr []T) {
	n := len(arr)

	// Build heap (rearrange array)
	// Start from last non-leaf node and go up to root
	for i := n/2 - 1; i >= 0; i-- {
		heapify(arr, n, i)
	}
}

// HeapSort sorts elements in ascending order using the heap sort algorithm.
// It first builds a max-heap, then repeatedly extracts the maximum element
// and places it at the end of the array.
func HeapSort[T constraints.Ordered](arr []T) {
	n := len(arr)

	if n <= 1 {
		return
	}

	// Build max heap
	BuildMaxHeap(arr)

	// Extract elements from heap one by one
	for i := n - 1; i > 0; i-- {
		// Move current root to end
		arr[0], arr[i] = arr[i], arr[0]

		// Call max heapify on the reduced heap
		heapify(arr, i, 0)
	}
}
