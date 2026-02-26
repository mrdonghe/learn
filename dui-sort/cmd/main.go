package main

import (
	"dui-sort"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

func parseInts(s string) ([]int, error) {
	s = strings.TrimSpace(s)
	if s == "" {
		return nil, nil
	}
	parts := strings.Split(s, ",")
	result := make([]int, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		n, err := strconv.Atoi(p)
		if err != nil {
			return nil, fmt.Errorf("invalid integer: %s", p)
		}
		result = append(result, n)
	}
	return result, nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <comma-separated-integers>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Example: %s 5,3,8,1,9,2,7,4,6\n", os.Args[0])
		os.Exit(1)
	}

	inputStr := os.Args[1]
	nums, err := parseInts(inputStr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	if len(nums) == 0 {
		fmt.Println("No numbers provided")
		os.Exit(0)
	}

	// Display unsorted input
	fmt.Printf("Input: %v\n", nums)

	// Record start time
	start := time.Now()

	// Perform heap sort
	duisort.HeapSort(nums)

	// Calculate elapsed time
	elapsed := time.Since(start)

	// Display sorted output
	fmt.Printf("Sorted: %v\n", nums)

	// Display timing information
	fmt.Printf("Time: %v\n", elapsed)
}
