package duisort

import (
	"fmt"
	"reflect"
	"testing"
)

func TestHeapSort(t *testing.T) {
	tests := []struct {
		name     string
		input    []int
		expected []int
	}{
		{
			name:     "empty slice",
			input:    []int{},
			expected: []int{},
		},
		{
			name:     "single element",
			input:    []int{1},
			expected: []int{1},
		},
		{
			name:     "already sorted",
			input:    []int{1, 2, 3, 4, 5},
			expected: []int{1, 2, 3, 4, 5},
		},
		{
			name:     "reverse sorted",
			input:    []int{5, 4, 3, 2, 1},
			expected: []int{1, 2, 3, 4, 5},
		},
		{
			name:     "with duplicates",
			input:    []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3},
			expected: []int{1, 1, 2, 3, 3, 4, 5, 5, 6, 9},
		},
		{
			name:     "random order",
			input:    []int{10, 7, 8, 9, 1, 5},
			expected: []int{1, 5, 7, 8, 9, 10},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := make([]int, len(tt.input))
			copy(input, tt.input)
			HeapSort(input)
			if !reflect.DeepEqual(input, tt.expected) {
				t.Errorf("HeapSort(%v) = %v, want %v", tt.input, input, tt.expected)
			}
		})
	}
}

func TestBuildMaxHeap(t *testing.T) {
	arr := []int{4, 10, 3, 5, 1}
	BuildMaxHeap(arr)
	// In a max-heap, root should be the maximum
	if arr[0] != 10 {
		t.Errorf("BuildMaxHeap: expected max 10 at root, got %d", arr[0])
	}
}

func TestHeapSortStrings(t *testing.T) {
	input := []string{"banana", "apple", "cherry", "date"}
	expected := []string{"apple", "banana", "cherry", "date"}
	HeapSort(input)
	if !reflect.DeepEqual(input, expected) {
		t.Errorf("HeapSort strings: got %v, want %v", input, expected)
	}
}

func TestHeapSortFloats(t *testing.T) {
	input := []float64{3.14, 1.41, 2.71, 1.62}
	expected := []float64{1.41, 1.62, 2.71, 3.14}
	HeapSort(input)
	if !reflect.DeepEqual(input, expected) {
		t.Errorf("HeapSort floats: got %v, want %v", input, expected)
	}
}

func ExampleHeapSort() {
	arr := []int{12, 11, 13, 5, 6, 7}
	HeapSort(arr)
	fmt.Println(arr)
	// Output: [5 6 7 11 12 13]
}

// TestHeapSortComprehensive tests all the required scenarios from feature_003
func TestHeapSortComprehensive(t *testing.T) {
	tests := []struct {
		name     string
		input    []int
		expected []int
	}{
		// Test sorting of empty slice
		{
			name:     "empty slice",
			input:    []int{},
			expected: []int{},
		},
		// Test sorting of single element slice
		{
			name:     "single element",
			input:    []int{1},
			expected: []int{1},
		},
		// Test sorting of already sorted slice (best case)
		{
			name:     "already sorted best case",
			input:    []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
			expected: []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
		},
		// Test sorting of reverse sorted slice (worst case)
		{
			name:     "reverse sorted worst case",
			input:    []int{10, 9, 8, 7, 6, 5, 4, 3, 2, 1},
			expected: []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
		},
		// Test sorting of slice with duplicate elements
		{
			name:     "with duplicates",
			input:    []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5},
			expected: []int{1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9},
		},
		// Test all same elements
		{
			name:     "all same elements",
			input:    []int{5, 5, 5, 5, 5},
			expected: []int{5, 5, 5, 5, 5},
		},
		// Test negative numbers
		{
			name:     "negative numbers",
			input:    []int{-5, -3, -1, -4, -2},
			expected: []int{-5, -4, -3, -2, -1},
		},
		// Test mixed positive and negative
		{
			name:     "mixed positive negative",
			input:    []int{-5, 3, -1, 4, 0, -2},
			expected: []int{-5, -2, -1, 0, 3, 4},
		},
		// Test large numbers
		{
			name:     "large numbers",
			input:    []int{1000000, 999999, 500000, 1},
			expected: []int{1, 500000, 999999, 1000000},
		},
		// Test two elements
		{
			name:     "two elements",
			input:    []int{2, 1},
			expected: []int{1, 2},
		},
		// Test three elements
		{
			name:     "three elements",
			input:    []int{3, 1, 2},
			expected: []int{1, 2, 3},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := make([]int, len(tt.input))
			copy(input, tt.input)
			HeapSort(input)
			if !reflect.DeepEqual(input, tt.expected) {
				t.Errorf("HeapSort(%v) = %v, want %v", tt.input, input, tt.expected)
			}
		})
	}
}

// TestHeapSortLargeRandom tests sorting of large random slices
func TestHeapSortLargeRandom(t *testing.T) {
	// Test with 1000 random elements
	input := make([]int, 1000)
	expected := make([]int, 1000)
	for i := 0; i < 1000; i++ {
		input[i] = i * 7 % 1000 // pseudo-random but deterministic
		expected[i] = input[i]
	}
	// Sort expected array using a simple method for comparison
	for i := 0; i < len(expected)-1; i++ {
		for j := 0; j < len(expected)-i-1; j++ {
			if expected[j] > expected[j+1] {
				expected[j], expected[j+1] = expected[j+1], expected[j]
			}
		}
	}

	HeapSort(input)

	if !reflect.DeepEqual(input, expected) {
		t.Errorf("HeapSort large random: sorting failed for 1000 elements")
	}

	// Test with 10000 elements
	inputLarge := make([]int, 10000)
	expectedLarge := make([]int, 10000)
	for i := 0; i < 10000; i++ {
		inputLarge[i] = i * 13 % 10000
		expectedLarge[i] = inputLarge[i]
	}
	for i := 0; i < len(expectedLarge)-1; i++ {
		for j := 0; j < len(expectedLarge)-i-1; j++ {
			if expectedLarge[j] > expectedLarge[j+1] {
				expectedLarge[j], expectedLarge[j+1] = expectedLarge[j+1], expectedLarge[j]
			}
		}
	}

	HeapSort(inputLarge)

	if !reflect.DeepEqual(inputLarge, expectedLarge) {
		t.Errorf("HeapSort large: sorting failed for 10000 elements")
	}
}

// TestHeapSortStability tests that heap sort handles various data patterns
func TestHeapSortStability(t *testing.T) {
	tests := []struct {
		name  string
		input []int
	}{
		{name: "sorted ascending", input: []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}},
		{name: "sorted descending", input: []int{10, 9, 8, 7, 6, 5, 4, 3, 2, 1}},
		{name: "zigzag pattern", input: []int{1, 10, 2, 9, 3, 8, 4, 7, 5, 6}},
		{name: "sawtooth pattern", input: []int{1, 2, 1, 2, 1, 2, 1, 2}},
		{name: "organ pipe pattern", input: []int{1, 2, 3, 4, 5, 5, 4, 3, 2, 1}},
		{name: "push front pattern", input: []int{10, 1, 2, 3, 4, 5, 6, 7, 8, 9}},
		{name: "sorted near", input: []int{1, 2, 3, 4, 5, 6, 7, 8, 10, 9}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := make([]int, len(tt.input))
			copy(input, tt.input)
			HeapSort(input)

			// Verify sorted
			for i := 1; i < len(input); i++ {
				if input[i-1] > input[i] {
					t.Errorf("HeapSort(%v): not sorted at index %d", tt.input, i)
					break
				}
			}
		})
	}
}


