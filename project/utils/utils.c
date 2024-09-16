#include "utils.h"

#include <stdint.h>
#include <stdio.h>

// Dummy function
int foo(void) { return 42; }

/**
 * @brief Parses a raw request into a nice struct
 *
 * @param request: A big string containing the request as it is received by the server
 * @param request_len: The size of the raw request
 * @param parsed : A struct that will contain the parsed request at the end of the function
 *
 * @note The variable `parsed` should be modified to store the parsed representation of the request.
 * @note `mat1`, `mat2` and `patterns` should point to the body of `request` at the location of each element.
*/
void parse_request(struct parsed_request *parsed, char *request, size_t request_len) {
    (void)parsed;
    (void)request;
    (void)request_len;
    printf("CHANGE ME\n");
}

/**
 * @brief Computes the product of two matrixes
 *
 * @param matrix1: a K x K matrix
 * @param matrix2: a K x K matrix
 * @param result: a K x K matrix that should contain the product of matrix1
 * and matrix2 at the end of the function
 * @param K: the size of the matrix
 *
 * @note `result` should be modified to the result of the multiplication of the matrices
*/
void multiply_matrix(uint32_t *matrix1, uint32_t *matrix2, uint32_t *result, uint32_t K) {
    (void)matrix1;
    (void)matrix2;
    (void)result;
    (void)K;
    return;
}

/**
 * @brief Computes a measure of similarity between the patterns and the matrix
 *
 * @param matrix: The matrix to search patterns in
 * @param matrix_size: The size of the matrix
 * @param patterns: The list of patterns
 * @param pattern_size: The size of each pattern
 * @param nb_patterns: The number of patterns
 * @param res: The result, the list of shortest distances for each pattern
 * @param K : The dimension of the file matrix
 *
 * @note `file` should be modified to contain the encrypted file.
*/
void test_patterns(uint32_t *matrix, uint32_t matrix_size, uint32_t *patterns,
                   uint32_t pattern_size, uint32_t nb_patterns, uint32_t *res) {
    (void)matrix;
    (void)matrix_size;
    (void)patterns;
    (void)pattern_size;
    (void)nb_patterns;
    (void)res;
    printf("CHANGE ME\n");
}

/**
 * @brief Converts an array of uint32_t to a comma separated string of the numbers
 *
 * @param str: The string used to store the response
 * @param res: The array to transform into a string
 * @param res_size: The length of the the array `res`
*/
void res_to_string(char *str, uint32_t *res, uint32_t res_size) { 
    (void)str;
    (void)res;
    (void)res_size;
    printf("CHANGE ME\n"); 
}

