package heapsort

// HeapSort sorts a slice of integers using the heap sort algorithm.
// It returns a new sorted slice, leaving the original unchanged.
func HeapSort(arr []int) []int {
	// Handle empty and single-element slices
	if len(arr) <= 1 {
		return append([]int{}, arr...)
	}

	// Create a copy to avoid modifying the original
	result := make([]int, len(arr))
	copy(result, arr)

	// Build max heap
	heapify(result)

	// Extract elements from heap one by one
	for i := len(result) - 1; i > 0; i-- {
		// Swap root (maximum) with the last element
		result[0], result[i] = result[i], result[0]

		// Restore heap property for the reduced heap
		siftDown(result, 0, i)
	}

	return result
}

// heapify builds a max heap from the given slice.
func heapify(arr []int) {
	// Start from the last non-leaf node and sift down each node
	// Last non-leaf node is at index (len(arr) / 2) - 1
	for i := len(arr)/2 - 1; i >= 0; i-- {
		siftDown(arr, i, len(arr))
	}
}

// siftDown maintains the max heap property by sifting down
// the element at index 'root' down to its proper position.
// 'heapSize' is the size of the heap to consider.
func siftDown(arr []int, root, heapSize int) {
	for {
		largest := root
		left := 2*root + 1
		right := 2*root + 2

		// Check if left child exists and is greater than current largest
		if left < heapSize && arr[left] > arr[largest] {
			largest = left
		}

		// Check if right child exists and is greater than current largest
		if right < heapSize && arr[right] > arr[largest] {
			largest = right
		}

		// If largest is still root, we're done
		if largest == root {
			break
		}

		// Swap root with the largest child
		arr[root], arr[largest] = arr[largest], arr[root]

		// Continue sifting down from the child position
		root = largest
	}
}
