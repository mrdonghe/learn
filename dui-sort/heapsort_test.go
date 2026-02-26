package heapsort

import (
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
			input:    []int{42},
			expected: []int{42},
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
			input:    []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5},
			expected: []int{1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9},
		},
		{
			name:     "random order",
			input:    []int{10, 3, 7, 1, 9, 2, 8, 4, 6, 5},
			expected: []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
		},
		{
			name:     "negative numbers",
			input:    []int{-5, 3, -2, 0, 7, -1, 4},
			expected: []int{-5, -2, -1, 0, 3, 4, 7},
		},
		{
			name:     "two elements",
			input:    []int{2, 1},
			expected: []int{1, 2},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := HeapSort(tt.input)
			if !reflect.DeepEqual(result, tt.expected) {
				t.Errorf("HeapSort(%v) = %v, want %v", tt.input, result, tt.expected)
			}
		})
	}
}

// Test that original slice is not modified
func TestHeapSortDoesNotModifyOriginal(t *testing.T) {
	original := []int{5, 3, 8, 1, 9, 2}
	originalCopy := make([]int, len(original))
	copy(originalCopy, original)

	HeapSort(original)

	if !reflect.DeepEqual(original, originalCopy) {
		t.Errorf("Original slice was modified: got %v, want %v", original, originalCopy)
	}
}
