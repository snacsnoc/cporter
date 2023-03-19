#include <stdio.h>

// Get the nth fibonacci number
long long fibonacci_iterative(int n)
{
    if (n <= 1) {
        return n;
    }

    long long prev = 0;
    long long current = 1;

    for (int i = 2; i <= n; i++) {
        long long next = prev + current;
        prev = current;
        current = next;
    }

    return current;
}
