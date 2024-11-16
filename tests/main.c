#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/resource.h> 
#include "../project/utils/utils.h"

void test_extract_number() {
    char str[] = "123,456,789";
    char delim = ',';
    char* end = str + sizeof(str);
    uint32_t number;
    size_t res = extract_number(str, delim, end, &number);
    if (res != 3) {
        printf("Error: extract_number returned %lu, expected 3\n", res);
        return;
    }
    if (number != 123) {
        printf("Error: extract_number returned %d, expected 123\n", number);
        return;
    }

    res = extract_number(str + 4, delim, end, &number);
    if (res != 3) {
        printf("Error: extract_number returned %lu, expected 3\n", res);
        return;
    }
    if (number != 456) {
        printf("Error: extract_number returned %d, expected 456\n", number);
        return;
    }

    printf("extract_number passed\n");
}//size_t extract_number(char *str, char delim, char* end, uint32_t* number);

void test_res_to_string() {
    uint32_t res[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    char str[100];
    res_to_string(str, res, 9);
    if (strcmp(str, "1,2,3,4,5,6,7,8,9") != 0) {
        printf("Error: res_to_string returned %s, expected 1,2,3,4,5,6,7,8,9\n", str);
        return;
    }

    printf("res_to_string passed\n");
}

void test_multiply_matrix() {
    uint32_t matrix1[] = {1, 2, 3, 4};
    uint32_t matrix2[] = {5, 6, 7, 8};
    uint32_t result[4];
    multiply_matrix(matrix1, matrix2, result, 2);
    if (result[0] != 19 || result[1] != 22 || result[2] != 43 || result[3] != 50) {
        printf("Error: multiply_matrix returned %d, %d, %d, %d, expected 19, 22, 43, 50\n", result[0], result[1], result[2], result[3]);
        return;
    }

    printf("multiply_matrix passed\n");
}

void test_test_patterns() {
    uint32_t matrix[] = {1, 2, 3, 4};
    uint32_t patterns[] = {1, 2};
    uint32_t res[2];
    test_patterns(matrix, 2, patterns, 2, 1, res);
    if (res[0] != 0 || res[1] != 8) {
        printf("Error: test_patterns returned %d, %d, expected 0, 8\n", res[0], res[1]);
        return;
    }

    printf("test_patterns passed\n");
}

void test_matrix_mult() {  
    uint32_t K = 5120;  // Example size
    uint32_t *matrix1 = (uint32_t *)malloc(K * K * sizeof(uint32_t));
    uint32_t *matrix2 = (uint32_t *)malloc(K * K * sizeof(uint32_t));
    uint32_t *result = (uint32_t *)malloc(K * K * sizeof(uint32_t));

    // Initialize matrix1 and matrix2 with some values
    srand((unsigned int)time(NULL));  // Seed the random number generator
    for (uint32_t i = 0; i < K * K; i++) {
        matrix1[i] = i % 100;  // Example values
        matrix2[i] = (i * 2) % 100;
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);  // Start time

    // Multiply matrices
    multiply_matrix(matrix1, matrix2, result, K);

    clock_gettime(CLOCK_MONOTONIC, &end);  // Start time
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Matrix multiplication took %f seconds\n", elapsed);

    // Free allocated memory
    free(matrix1);
    free(matrix2);
    free(result);
}

int main() {
# if 0
    test_extract_number();
    test_res_to_string();
    test_multiply_matrix();
    test_test_patterns();
    #endif
    test_matrix_mult();

    return 0;
}
