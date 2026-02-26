package heapsort

import (
	"math/rand"
	"testing"
)

// BenchmarkHeapSortRandom100 benchmarks heap sort with 100 random elements
func BenchmarkHeapSortRandom100(b *testing.B) {
	data := make([]int, 100)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortRandom1000 benchmarks heap sort with 1000 random elements
func BenchmarkHeapSortRandom1000(b *testing.B) {
	data := make([]int, 1000)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortRandom10000 benchmarks heap sort with 10000 random elements
func BenchmarkHeapSortRandom10000(b *testing.B) {
	data := make([]int, 10000)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortRandom100000 benchmarks heap sort with 100000 random elements
func BenchmarkHeapSortRandom100000(b *testing.B) {
	data := make([]int, 100000)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortSorted benchmarks heap sort with already sorted input
func BenchmarkHeapSortSorted1000(b *testing.B) {
	data := make([]int, 1000)
	for i := range data {
		data[i] = i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortSorted10000 benchmarks heap sort with already sorted input
func BenchmarkHeapSortSorted10000(b *testing.B) {
	data := make([]int, 10000)
	for i := range data {
		data[i] = i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortSorted100000 benchmarks heap sort with already sorted input
func BenchmarkHeapSortSorted100000(b *testing.B) {
	data := make([]int, 100000)
	for i := range data {
		data[i] = i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortReverseSorted benchmarks heap sort with reverse sorted input
func BenchmarkHeapSortReverseSorted1000(b *testing.B) {
	data := make([]int, 1000)
	for i := range data {
		data[i] = 1000 - i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortReverseSorted10000 benchmarks heap sort with reverse sorted input
func BenchmarkHeapSortReverseSorted10000(b *testing.B) {
	data := make([]int, 10000)
	for i := range data {
		data[i] = 10000 - i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortReverseSorted100000 benchmarks heap sort with reverse sorted input
func BenchmarkHeapSortReverseSorted100000(b *testing.B) {
	data := make([]int, 100000)
	for i := range data {
		data[i] = 100000 - i
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortSmall100 benchmarks heap sort with 100 elements
func BenchmarkHeapSortSmall100(b *testing.B) {
	data := make([]int, 100)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}

// BenchmarkHeapSortSmall500 benchmarks heap sort with 500 elements
func BenchmarkHeapSortSmall500(b *testing.B) {
	data := make([]int, 500)
	for i := range data {
		data[i] = rand.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		HeapSort(data)
	}
}
