#ifndef UTILS_H
#define UTILS_H

#include "utils.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define BLOCK_SIZE 64

void parse_request(struct parsed_request *parsed, char *request, size_t request_len);
void multiply_matrix(uint32_t *matrix1, uint32_t *matrix2, uint32_t *result, uint32_t K);
void test_patterns(uint32_t *matrix, uint32_t matrix_size, uint32_t *patterns, uint32_t pattern_size, uint32_t nb_patterns, uint32_t *res);
void res_to_string(char *str, uint32_t *res, uint32_t res_size);
char *complete_algorithm(char *raw_request, uint32_t raw_request_len, char *res_str, uint32_t *res_uint, uint32_t *intermediary_matrix, uint32_t *resp_len);
uint32_t extract_number(char **str);

uint32_t extract_number(char **str) {
    uint32_t number = strtoul(*str, (char**)str, 10);
    if (**str == ',') {
        (*str)++;  
    }
    return number;
}


void get_positions(uint32_t *mat1, uint32_t *mat2, uint32_t *patterns, char *request, size_t request_len) {
    int count = 0;
    //fix compile flag :)
    (void)mat1;
    (void)mat2;
    (void)patterns;
    for (size_t i = 0; i < request_len; i++) {
        if (request[i] == ',') {
            void* temp = &request[i + 1];
            switch (count) {
                case 0:
                    mat1 = temp;
                    break;
                case 1:
                    mat2 = temp;
                    break;
                case 2:
                    patterns = temp;
                    break;
            }
            count++;
        }
        if (count == 3)
            break;
    }
}

void test_parse_request(struct parsed_request *parsed, char *request, size_t request_len) {
    uint32_t matrixSideSize, nbPatterns, sizeOfEachPattern;

    sscanf(request, "%u,%u,%u", &matrixSideSize, &nbPatterns, &sizeOfEachPattern);
    get_positions(parsed->mat1, parsed->mat2, parsed->patterns, request, request_len);
    parsed->nb_patterns = nbPatterns;
    parsed->patterns_size = sizeOfEachPattern;
}

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
    //      MatrixSideSize,NbPatterns,SizeOfEachPattern,Text..NetworkLayer..Pattern1..PatternN
    // e.g. 2,2,1,ThisIsAnExample!SomeNetworkLayerExamJump

    PRINTF("=== Parsing request ===\n", 0);
    PRINTF("request: %s\n", request);
    parsed->matrices_size = extract_number(&request);
    PRINTF("matrices_size: %d\n", parsed->matrices_size);
    PRINTF("request delta: %lu\n", request - r);
    parsed->nb_patterns = extract_number(&request);
    PRINTF("nb_patterns: %d\n", parsed->nb_patterns);
    PRINTF("request delta: %lu\n", request - r);
    parsed->patterns_size = extract_number(&request);
    PRINTF("patterns_size: %d\n", parsed->patterns_size);
    PRINTF("request delta: %lu\n", request - r);

    // The text and network layer are of the same size.
    const size_t text_len = parsed->matrices_size * parsed->matrices_size * sizeof(uint32_t);
    PRINTF("text_len: %lu\n", text_len);
    // const size_t pattern_len = parsed->patterns_size * sizeof(uint32_t);

    size_t left_len = request_len - (request - request);
    if (left_len < text_len * 2 + parsed->nb_patterns * parsed->patterns_size)
        return;
    
    char temp[text_len];
    parsed->mat1 = (uint32_t*)request;
    strncpy(temp, request, text_len);
    PRINTF("mat1: %s\n", temp);
    for (uint32_t i = 0; i < text_len / 4; i++) {
        //PRINTF("%u ", parsed->mat1[i]);
    }
    request += text_len;
    PRINTF("request delta: %lu\n", request - r);
    
    parsed->mat2 = (uint32_t*)request;
    strncpy(temp, request, text_len);
    PRINTF("mat2: %s\n", temp);
    request += text_len;
    PRINTF("request delta: %lu\n", request - r);
    
    parsed->patterns = (uint32_t*)request;
    for (uint32_t i = 0; i < parsed->nb_patterns; i++) {
        strncpy(temp, request + i * parsed->patterns_size, parsed->patterns_size);
        //PRINTF("patterns: %s\n", temp);
    }

    //request += parsed->nb_patterns * parsed->patterns_size;
    //printf("request delta: %lu\n", request - r);

    // print all addresses in memory
    PRINTF("mat1: %p\n", (void*)parsed->mat1);
    PRINTF("mat2: %p\n", (void*)parsed->mat2);
    PRINTF("patterns: %p\n", (void*)parsed->patterns);
    PRINTF("=== End of parsing ===\n", 0);
}

void transpose_matrix(const uint32_t *matrix, uint32_t *transposed, uint32_t K) {
    for (uint32_t i = 0; i < K; i++) {
        for (uint32_t j = 0; j < K; j++) {
            transposed[j * K + i] = matrix[i * K + j];
        }
    }
}

/**
 * @brief Computes the product of two matrixes
 *>
 * @param matrix1: a K x K matrix
 * @param matrix2: a K x K matrix
 * @param result: a K x K matrix that should contain the product of matrix1
 * and matrix2 at the end of the function
 * @param K: the size of the matrix
 *
 * @note `result` should be modified to the result of the multiplication of the matrices
*/
void multiply_matrix(uint32_t *matrix1, uint32_t *matrix2, uint32_t *result, uint32_t K) {
    // i is the row index
    // j is the column index
    // k is the index of the element in the row/column
    memset(result, 0, K * K * sizeof(uint32_t));
    for (uint32_t i = 0; i < K; i++) {
        for (uint32_t j = 0; j < K; j++) {
#if defined(BEST)
            uint32_t transposed_matrix2[K * K];
            transpose_matrix(matrix2, transposed_matrix2, K);

            for (uint32_t i = 0; i < K; i++) {
                for (uint32_t j = 0; j < K / 4 * 4; j++) {
                    uint32_t sum0 = 0, sum1 = 0, sum2 = 0, sum3 = 0;
                    for (uint32_t k = 0; k < K; k += 4) {
                        sum0 += matrix1[i * K + k] * transposed_matrix2[j * K + k];
                        sum1 += matrix1[i * K + k + 1] * transposed_matrix2[j * K + k + 1];
                        sum2 += matrix1[i * K + k + 2] * transposed_matrix2[j * K + k + 2];
                        sum3 += matrix1[i * K + k + 3] * transposed_matrix2[j * K + k + 3];
                    }
                    result[i * K + j] = sum0 + sum1 + sum2 + sum3;
                }

                for (uint32_t j = K / 4 * 4; j < K; j++) {
                    for (uint32_t k = 0; k < K; k++) {
                        result[i * K + j] += matrix1[i * K + k] * transposed_matrix2[j * K + k];
                    }
                }
            }
#elif defined(UNROLL)
            for (uint32_t k = 0; k < K / 4 * 4; k += 4) {
#if defined(CACHE_AWARE)
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
                result[i * K + j] += matrix1[i * K + k + 1] * matrix2[(k + 1) * K + j];
                result[i * K + j] += matrix1[i * K + k + 2] * matrix2[(k + 2) * K + j];
                result[i * K + j] += matrix1[i * K + k + 3] * matrix2[(k + 3) * K + j];
#else
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
                result[i * K + j] += matrix1[i * K + k + 1] * matrix2[(k + 1) * K + j];
                result[i * K + j] += matrix1[i * K + k + 2] * matrix2[(k + 2) * K + j];
                result[i * K + j] += matrix1[i * K + k + 3] * matrix2[(k + 3) * K + j];
#endif
            }

            for (uint32_t k = K / 4 * 4; k < K; k++) {
#if defined(CACHE_AWARE)
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
#else
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
#endif
            }

#elif defined(CACHE_AWARE)
            for (uint32_t k = 0; k < K; k++) {
                result[i * K + j] += matrix1[i * K + j] * matrix2[j * K + k];
            }
#else       // Default
            for (uint32_t k = 0; k < K; k++) {
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
            }
#endif
        }
    }
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
    const uint32_t m = matrix_size * matrix_size;
    const uint32_t n = nb_patterns;
    
    if (res == NULL) {
        return;
    }

    for (uint32_t i = 0; i < n; i++) {
        res[i] = UINT32_MAX;
    }

    for (uint32_t i = 0; i < m - pattern_size + 1; i++) {
        for (uint32_t j = 0; j < n; j++) {
            uint32_t dist = 0;
            uint32_t new_j = j * pattern_size;
            for (uint32_t k = 0; k < pattern_size; k++) {
                dist += (matrix[i + k] - patterns[new_j + k]) * (matrix[i + k] - patterns[new_j + k]);
            }

            if (dist < res[j]) {
                res[j] = dist;
            }
        }
    }
}

/**
 * @brief Converts an array of uint32_t to a comma separated string of the numbers
 *
 * @param str: The string used to store the response
 * @param res: The array to transform into a string
 * @param res_size: The length of the the array `res`
*/
void res_to_string(char *str, uint32_t *res, uint32_t res_size) { 
    for (uint32_t i = 0; i < res_size; i++) {
        sprintf(str, "%d", res[i]);
        str += strlen(str);
        if (i != res_size - 1) {
            sprintf(str, ",");
            str += strlen(str);
        }
    }
}

/**
 * @brief Applies the complete algorithm
 *
 * @param raw_request The raw request as it is received by the server
 * @param raw_request_len The size of the raw request
 * @param res_str The output of the function => First return value
 * @param res_uint Intermeditary storage you can use for the computation of the distance for the pattern before the string transformation
 * @param intermediary_matrix Param you can use to store the result of the product between the two matrices
 * @param resp_len the length of the resres_charponse => Second return value
 *
 * @note you can assume that `res_str`, `res_uint` and `intermediary_matrix` are big enough to store what you need
 * @note res_str has a size of 2**16, res_uint can old 2*10 uint32_t and intermediary_matrix can hold 2*10 uint32_t, this should be more than enough
*/
char *complete_algorithm(char *raw_request, uint32_t raw_request_len, char *res_str, uint32_t *res_uint, uint32_t *intermediary_matrix, uint32_t *resp_len) {
    if (!raw_request || raw_request_len == 0) {
        return NULL;
    }
    
    struct parsed_request parsed;
    test_parse_request(&parsed, raw_request, raw_request_len);

    multiply_matrix(parsed.mat1, parsed.mat2, intermediary_matrix, parsed.matrices_size);

    test_patterns(intermediary_matrix, parsed.matrices_size, parsed.patterns,parsed.patterns_size, parsed.nb_patterns, res_uint);

    res_to_string(res_str, res_uint, parsed.nb_patterns);

    *resp_len = strlen(res_str);
    //printf("resp_len: %d\n", *resp_len);

    return res_str;
}
#endif 