package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"

	"dui-sort/heapsort"
)

func main() {
	var numbers []int

	// Check if command line arguments are provided
	if len(os.Args) > 1 {
		// Parse from command line arguments
		numbers = parseArgs(os.Args[1:])
	} else {
		// Read from stdin
		numbers = parseStdin()
	}

	// Handle empty input
	if len(numbers) == 0 {
		fmt.Fprintln(os.Stderr, "Error: no input provided")
		fmt.Fprintln(os.Stderr, "Usage: cli [numbers...] or echo [numbers...] | cli")
		os.Exit(1)
	}

	// Sort the numbers
	sorted := heapsort.HeapSort(numbers)

	// Output the sorted result
	for i, n := range sorted {
		if i > 0 {
			fmt.Print(" ")
		}
		fmt.Print(n)
	}
	fmt.Println()
}

// parseArgs parses integer arguments from command line
func parseArgs(args []string) []int {
	var numbers []int

	for _, arg := range args {
		// Handle space-separated numbers in a single argument
		parts := strings.Fields(arg)
		for _, part := range parts {
			n, err := strconv.Atoi(part)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: invalid integer: %s\n", part)
				os.Exit(1)
			}
			numbers = append(numbers, n)
		}
	}

	return numbers
}

// parseStdin reads integers from stdin
func parseStdin() []int {
	var numbers []int

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		for _, part := range parts {
			n, err := strconv.Atoi(part)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: invalid integer: %s\n", part)
				os.Exit(1)
			}
			numbers = append(numbers, n)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input: %v\n", err)
		os.Exit(1)
	}

	return numbers
}
