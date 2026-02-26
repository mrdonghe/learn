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


// HeapPush adds an element to the heap and maintains the max-heap property.
// It appends the element and then "sifts up" to restore heap property.
func HeapPush[T constraints.Ordered](arr []T, value T) []T {
	// Append the new element to the end of the array
	arr = append(arr, value)

	// Sift up: move the new element to its correct position
	i := len(arr) - 1
	for i > 0 {
		parent := (i - 1) / 2
		if arr[i] <= arr[parent] {
			break
		}
		arr[i], arr[parent] = arr[parent], arr[i]
		i = parent
	}

	return arr
}

// HeapPop removes and returns the maximum element from the heap.
// It replaces the root with the last element and then "sifts down" to restore heap property.
// Returns the removed element and the modified slice.
// Note: The caller is responsible for handling the returned slice (it may be empty).
func HeapPop[T constraints.Ordered](arr []T) (T, []T) {
	if len(arr) == 0 {
		var zero T
		return zero, arr
	}

	// Store the max element (root)
	max := arr[0]

	// Move the last element to the root
	last := arr[len(arr)-1]
	arr = arr[:len(arr)-1]

	if len(arr) > 0 {
		arr[0] = last
		// Sift down: restore max-heap property
		heapify(arr, len(arr), 0)
	}

	return max, arr
}

// HeapSize returns the number of elements in the heap.
func HeapSize[T any](arr []T) int {
	return len(arr)
}

// HeapEmpty returns true if the heap has no elements.
func HeapEmpty[T any](arr []T) bool {
	return len(arr) == 0
}