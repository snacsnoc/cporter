/* string_lib.c */

#include <stdlib.h>
#include <string.h>

char* create_string(const char* input) {
    size_t len = strlen(input);
    char* result = (char*)malloc((len + 1) * sizeof(char));
    if (result != NULL) {
        strcpy(result, input);
    }
    return result;
}

void free_string(char* str) {
    if (str != NULL) {
        free(str);
    }
}
