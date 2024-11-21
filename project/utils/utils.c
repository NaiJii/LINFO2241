#ifndef UTILS_H
#define UTILS_H

#include "utils.h"

#define MULTITHREAD
// Blocking size for matrix multiplication
// BLOCK_SIZE of less than 8 will not work because in our matrix multiplication thread, we unroll the loop by 8.
// This could be fixed by unrolling less
#define BLOCK_SIZE 8
#define min(a, b) (((a)<(b))?(a):(b))

// Loop unrolling with cache awareness
#define LOOP_UNROLL(result, i, j, k, K, matrix1, matrix2) \
    for (k = 0; k + 8 <= K; k += 8) { \
        result[i * K + k] += matrix1[i * K + j] * matrix2[j * K + k]; \
        result[i * K + k + 1] += matrix1[i * K + j] * matrix2[j * K + k + 1]; \
        result[i * K + k + 2] += matrix1[i * K + j] * matrix2[j * K + k + 2]; \
        result[i * K + k + 3] += matrix1[i * K + j] * matrix2[j * K + k + 3]; \
        result[i * K + k + 4] += matrix1[i * K + j] * matrix2[j * K + k + 4]; \
        result[i * K + k + 5] += matrix1[i * K + j] * matrix2[j * K + k + 5]; \
        result[i * K + k + 6] += matrix1[i * K + j] * matrix2[j * K + k + 6]; \
        result[i * K + k + 7] += matrix1[i * K + j] * matrix2[j * K + k + 7]; \
    } \
    for (; k < K; k++) { \
        result[i * K + k] += matrix1[i * K + j] * matrix2[j * K + k]; \
    }

// Loop unrolling without cache awareness
#define LOOP_UNROLL_INEFFICIENT(result, i, j, k, K, matrix1, matrix2) \
    for (k = 0; k + 8 <= K; k += 8) { \
        result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 1] * matrix2[(k + 1) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 2] * matrix2[(k + 2) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 3] * matrix2[(k + 3) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 4] * matrix2[(k + 4) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 5] * matrix2[(k + 5) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 6] * matrix2[(k + 6) * K + j]; \
        result[i * K + j] += matrix1[i * K + k + 7] * matrix2[(k + 7) * K + j]; \
    } \
    for (; k < K; k++) { \
        result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j]; \
    }

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

    PRINTF("=== Parsing request ===\n");
    PRINTF("request: %s\n", request);
    parsed->matrices_size = extract_number(&request);
    PRINTF("matrices_size: %d\n", parsed->matrices_size);
    parsed->nb_patterns = extract_number(&request);
    PRINTF("nb_patterns: %d\n", parsed->nb_patterns);
    parsed->patterns_size = extract_number(&request);
    PRINTF("patterns_size: %d\n", parsed->patterns_size);

    // The text and network layer are of the same size.
    const size_t text_len = parsed->matrices_size * parsed->matrices_size * sizeof(uint32_t);
    PRINTF("text_len: %lu\n", text_len);
    // const size_t pattern_len = parsed->patterns_size * sizeof(uint32_t);

    size_t left_len = request_len - (request - request);
    if (left_len < text_len * 2 + parsed->nb_patterns * parsed->patterns_size)
        return;
    
    parsed->mat1 = (uint32_t*)request;
    request += text_len;
    
    parsed->mat2 = (uint32_t*)request;
    request += text_len;
    
    parsed->patterns = (uint32_t*)request;

    //request += parsed->nb_patterns * parsed->patterns_size;
    //printf("request delta: %lu\n", request - r);

    // print all addresses in memory
    PRINTF("mat1: %p\n", (void*)parsed->mat1);
    PRINTF("mat2: %p\n", (void*)parsed->mat2);
    PRINTF("patterns: %p\n", (void*)parsed->patterns);
    PRINTF("=== End of parsing ===\n");
}

void *multiply_matrix_thread(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    uint32_t *matrix1 = data->matrix1;
    uint32_t *matrix2 = data->matrix2;
    uint32_t *result = data->result;
    uint32_t K = data->K;
    uint32_t iBlock = data->i;
    uint32_t kBlock = data->k;
    uint32_t jBlock = data->j;

    for (uint32_t i = iBlock; i < min(iBlock + BLOCK_SIZE, K); i++) {
        for (uint32_t k = kBlock; k < min(kBlock + BLOCK_SIZE, K); k++) {
            uint32_t a_val = matrix1[i * K + k];
            __builtin_prefetch(&matrix1[(i + 1) * K + k], 0, 1); // Prefetch next row of matrix1

            uint32_t *b_ptr = &matrix2[k * K + jBlock];
            uint32_t *r_ptr = &result[i * K + jBlock];

            for (uint32_t j = 0; j < BLOCK_SIZE; j += 8) {
                if (jBlock + j + 7 < K) {
                    // Prefetch next block of matrix2
                    __builtin_prefetch(&b_ptr[j + 8], 0, 1);
                    
                    // Unrolling loop by 8
                    r_ptr[j] += a_val * b_ptr[j];
                    r_ptr[j + 1] += a_val * b_ptr[j + 1];
                    r_ptr[j + 2] += a_val * b_ptr[j + 2];
                    r_ptr[j + 3] += a_val * b_ptr[j + 3];
                    r_ptr[j + 4] += a_val * b_ptr[j + 4];
                    r_ptr[j + 5] += a_val * b_ptr[j + 5];
                    r_ptr[j + 6] += a_val * b_ptr[j + 6];
                    r_ptr[j + 7] += a_val * b_ptr[j + 7];
                } else { // Handle case when jBlock + j + 7 exceeds K
                    for (uint32_t jj = 0; jj < 8 && jBlock + j + jj < K; jj++) {
                        r_ptr[j + jj] += a_val * b_ptr[j + jj];
                    }
                }

                // Prefetch next block of result
                __builtin_prefetch(&r_ptr[j + 8], 1, 1);
            }
        }
    }

    pthread_exit(NULL);
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
#if defined(MULTITHREAD) 
    uint32_t num_blocks = ( K + BLOCK_SIZE - 1 ) / BLOCK_SIZE; 
    PRINTF("num_blocks: %d = (%d + %d - 1) / %d\n", num_blocks, K, BLOCK_SIZE, BLOCK_SIZE);
    uint32_t num_threads = num_blocks * num_blocks; 

    pthread_t threads[num_threads];
    struct thread_data thread_data[num_threads];
    PRINTF("num_threads: %d\n", num_threads);
    
    uint32_t t = 0;
    
    for (uint32_t iBlock = 0; iBlock < K; iBlock += BLOCK_SIZE) {
        for (uint32_t kBlock = 0; kBlock < K; kBlock += BLOCK_SIZE) {
            for (uint32_t jBlock = 0; jBlock < K; jBlock += BLOCK_SIZE) {
                if (t < num_threads) {
                    thread_data[t].matrix1 = matrix1;
                    thread_data[t].matrix2 = matrix2;
                    thread_data[t].result = result;
                    thread_data[t].K = K;
                    thread_data[t].i = iBlock;
                    thread_data[t].k = kBlock;
                    thread_data[t].j = jBlock;

                    PRINTF("Creating thread %d\n", t);
                    pthread_create(&threads[t], NULL, multiply_matrix_thread, &thread_data[t]);
                    t++;
                }
            }
        }
    }

    // Wait for all threads to complete
    for (uint32_t i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
#else 
#if defined (BEST)
    for (uint32_t iBlock = 0; iBlock < K; iBlock += BLOCK_SIZE) {
        for (uint32_t kBlock = 0; kBlock < K; kBlock += BLOCK_SIZE) { 
            for (uint32_t jBlock = 0; jBlock < K; jBlock += BLOCK_SIZE) {
                for (uint32_t i = iBlock; i < min(iBlock + BLOCK_SIZE, K); i++) {
                    for (uint32_t k = kBlock; k < min(kBlock + BLOCK_SIZE, K); k++) {
                        uint32_t a_val = matrix1[i * K + k];
                        __builtin_prefetch(&matrix1[(i + 1) * K + k], 0, 1);

                        uint32_t *b_ptr = &matrix2[k * K + jBlock];
                        uint32_t *r_ptr = &result[i * K + jBlock];
                        for (uint32_t j = 0; j < BLOCK_SIZE; j += 8) {
                            if (jBlock + j + 7 < K) {
                                __builtin_prefetch(&b_ptr[j + 8], 0, 1);
                                r_ptr[j] += a_val * b_ptr[j];
                                r_ptr[j + 1] += a_val * b_ptr[j + 1];
                                r_ptr[j + 2] += a_val * b_ptr[j + 2];
                                r_ptr[j + 3] += a_val * b_ptr[j + 3];
                                r_ptr[j + 4] += a_val * b_ptr[j + 4];
                                r_ptr[j + 5] += a_val * b_ptr[j + 5];
                                r_ptr[j + 6] += a_val * b_ptr[j + 6];
                                r_ptr[j + 7] += a_val * b_ptr[j + 7];
                            } else { // unrolling exceeds K
                                for (uint32_t jj = 0; jj < 8 && jBlock + j + jj < K; jj++) {
                                    r_ptr[j + jj] += a_val * b_ptr[j + jj];
                                }
                            }

                            __builtin_prefetch(&r_ptr[j + 8], 1, 1);
                        }
                    }
                }
            }
        }
    }
#else
    for (uint32_t i = 0; i < K; i++) {
        for (uint32_t j = 0; j < K; j++) {
            uint32_t k = 0;
#if defined(UNROLL) && defined(CACHE_AWARE)
            LOOP_UNROLL(result, i, j, k, K, matrix1, matrix2);
#elif defined(UNROLL) && !defined(CACHE_AWARE)
            LOOP_UNROLL_INEFFICIENT(result, i, j, k, K, matrix1, matrix2);
#elif defined(CACHE_AWARE)
            for (; k < K; k++) {
                result[i * K + k] += matrix1[i * K + j] * matrix2[j * K + k];
            }
#else       // Default
            for (; k < K; k++) {
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
            }
#endif
        }
    }
#endif
#endif
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
 *
 * @note `file` should be modified to contain the encrypted file.
*/
void test_patterns(uint32_t *matrix, uint32_t matrix_size, uint32_t *patterns,
                   uint32_t pattern_size, uint32_t nb_patterns, uint32_t *res) {
    const uint32_t m = matrix_size * matrix_size;
    
    for (uint32_t i = 0; i < nb_patterns; i++) {
        res[i] = UINT32_MAX;
    }

    for (uint32_t i = 0; i < m - pattern_size + 1; i++) {
        for (uint32_t j = 0; j < nb_patterns; j++) {
            uint32_t dist = 0;
            uint32_t new_j = j * pattern_size;
            uint32_t k = 0;

            __builtin_prefetch(&patterns[new_j], 0, 1);

#if defined(UNROLL) || defined(BEST)
            for (; k + 4 <= pattern_size; k += 4) {
                uint32_t diff0 = matrix[i + k] - patterns[new_j + k];
                uint32_t diff1 = matrix[i + k + 1] - patterns[new_j + k + 1];
                uint32_t diff2 = matrix[i + k + 2] - patterns[new_j + k + 2];
                uint32_t diff3 = matrix[i + k + 3] - patterns[new_j + k + 3];
                dist += diff0 * diff0 + diff1 * diff1 + diff2 * diff2 + diff3 * diff3;

                __builtin_prefetch(&matrix[i + k + 4], 0, 1);
                __builtin_prefetch(&patterns[new_j + k + 4], 0, 1);
            }
#endif
            for (; k < pattern_size; k++) {
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
        str += sprintf(str, "%d", res[i]);
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
    parse_request(&parsed, raw_request, raw_request_len);

    multiply_matrix(parsed.mat1, parsed.mat2, intermediary_matrix, parsed.matrices_size);

    test_patterns(intermediary_matrix, parsed.matrices_size, parsed.patterns,parsed.patterns_size, parsed.nb_patterns, res_uint);

    res_to_string(res_str, res_uint, parsed.nb_patterns);

    *resp_len = strlen(res_str);
    //printf("resp_len: %d\n", *resp_len);

    return res_str;
}
#endif 