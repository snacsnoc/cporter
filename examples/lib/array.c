#include <stddef.h>
/* sum of squares */
long long sum_of_squares(const int* arr, size_t n) {
    long long result = 0;
    for (size_t i = 0; i < n; ++i) {
        result += (long long)arr[i] * arr[i];
    }
    return result;
}