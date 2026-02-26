package heapsort

import (
	"sort"
	"testing"
)

func TestGenericHeapSort(t *testing.T) {
	tests := []struct {
		name string
		data []int
	}{
		{"empty slice", []int{}},
		{"single element", []int{1}},
		{"two elements", []int{2, 1}},
		{"already sorted", []int{1, 2, 3, 4, 5}},
		{"reverse sorted", []int{5, 4, 3, 2, 1}},
		{"random", []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5}},
		{"with duplicates", []int{3, 3, 3, 1, 1, 2, 2}},
		{"negative numbers", []int{-5, -3, -1, -4, -2}},
		{"mixed positive and negative", []int{-5, 3, -1, 4, 0}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data := make([]int, len(tt.data))
			copy(data, tt.data)

			GenericHeapSort(data, func(a, b int) bool { return a < b })

			if !sort.IntsAreSorted(data) {
				t.Errorf("expected sorted slice, got %v", data)
			}
		})
	}
}

func TestSorted(t *testing.T) {
	original := []int{3, 1, 4, 1, 5}
	result := Sorted(original, func(a, b int) bool { return a < b })

	// Original should be unchanged
	if len(original) != 5 {
		t.Errorf("original was modified, got %v", original)
	}

	// Result should be sorted
	if !sort.IntsAreSorted(result) {
		t.Errorf("expected sorted slice, got %v", result)
	}
}

func TestHeapSortFunc(t *testing.T) {
	data := []int{5, 4, 3, 2, 1}
	HeapSortFunc(data, func(a, b int) bool { return a < b })

	if !sort.IntsAreSorted(data) {
		t.Errorf("expected sorted slice, got %v", data)
	}
}

func TestIntHeap(t *testing.T) {
	h := IntHeap{5, 3, 1, 4, 2}
	sort.Sort(&h)

	if h[0] != 1 || h[4] != 5 {
		t.Errorf("expected [1 2 3 4 5], got %v", h)
	}
}

func TestReverseIntHeap(t *testing.T) {
	h := ReverseIntHeap{1, 2, 3, 4, 5}
	sort.Sort(&h)

	if h[0] != 5 || h[4] != 1 {
		t.Errorf("expected [5 4 3 2 1], got %v", h)
	}
}

func TestStringHeap(t *testing.T) {
	h := StringHeap{"banana", "apple", "cherry"}
	sort.Sort(&h)

	if h[0] != "apple" || h[2] != "cherry" {
		t.Errorf("expected [apple banana cherry], got %v", h)
	}
}

func TestFloat64Heap(t *testing.T) {
	h := Float64Heap{3.14, 1.41, 2.71, 1.62}
	sort.Sort(&h)

	if h[0] != 1.41 || h[3] != 3.14 {
		t.Errorf("expected [1.41 1.62 2.71 3.14], got %v", h)
	}
}

func TestGenericHeapWithCustomType(t *testing.T) {
	type Person struct {
		name string
		age  int
	}

	people := []Person{
		{"Alice", 30},
		{"Bob", 25},
		{"Charlie", 35},
	}

	// Sort by age
	GenericHeapSort(people, func(a, b Person) bool { return a.age < b.age })

	if people[0].age != 25 || people[2].age != 35 {
		t.Errorf("expected sorted by age, got %v", people)
	}
}

func TestGenericHeapSortDescending(t *testing.T) {
	data := []int{1, 5, 2, 6, 3}
	GenericHeapSort(data, func(a, b int) bool { return a > b })

	expected := []int{6, 5, 3, 2, 1}
	for i := range data {
		if data[i] != expected[i] {
			t.Errorf("expected %v, got %v", expected, data)
			break
		}
	}
}
