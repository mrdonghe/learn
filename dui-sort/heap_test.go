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
