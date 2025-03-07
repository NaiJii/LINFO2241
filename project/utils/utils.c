#include "utils.h"

#if defined SIMD
#include "simd.h"
#elif defined SIMT
#include "simt.h"
#endif

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
    multiply_matrix_data_t *data = (multiply_matrix_data_t *)arg;
    uint32_t *matrix1 = data->matrix1;
    uint32_t *matrix2 = data->matrix2;
    uint32_t *result = data->result;
    uint32_t K = data->K;
    uint32_t start_row = data->start_row;
    uint32_t end_row = data->end_row;

    for (uint32_t iBlock = start_row; iBlock < end_row; iBlock += BLOCK_SIZE) {
        for (uint32_t kBlock = 0; kBlock < K; kBlock += BLOCK_SIZE) {
            for (uint32_t jBlock = 0; jBlock < K; jBlock += BLOCK_SIZE) {
                for (uint32_t i = iBlock; i < min(iBlock + BLOCK_SIZE, end_row); i++) {
                    for (uint32_t k = kBlock; k < min(kBlock + BLOCK_SIZE, K); k++) {
                        uint32_t a_val = matrix1[i * K + k];
                        __builtin_prefetch(&matrix1[(i + 1) * K + k], 0, 1);
                        uint32_t *b_ptr = &matrix2[k * K + jBlock];
                        uint32_t *r_ptr = &result[i * K + jBlock];
                        
                        for (uint32_t j = 0; j < BLOCK_SIZE && (jBlock + j) < K; j += 8) {
                            if (j + 7 < BLOCK_SIZE && jBlock + j + 7 < K) {
                                __builtin_prefetch(&b_ptr[j + 8], 0, 1);
                                r_ptr[j] += a_val * b_ptr[j];
                                r_ptr[j + 1] += a_val * b_ptr[j + 1];
                                r_ptr[j + 2] += a_val * b_ptr[j + 2];
                                r_ptr[j + 3] += a_val * b_ptr[j + 3];
                                r_ptr[j + 4] += a_val * b_ptr[j + 4];
                                r_ptr[j + 5] += a_val * b_ptr[j + 5];
                                r_ptr[j + 6] += a_val * b_ptr[j + 6];
                                r_ptr[j + 7] += a_val * b_ptr[j + 7];
                            } else {
                                for (uint32_t jj = 0; jj < 8 && jBlock + j + jj < K; jj++) {
                                    r_ptr[j + jj] += a_val * b_ptr[j + jj];
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return NULL;
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
#if defined(SIMT)
        multiply_matrix_simt(matrix1, matrix2, result, K);
#else

    // i is the row index
    // j is the column index
    // k is the index of the element in the row/column
    memset(result, 0, K * K * sizeof(uint32_t));
#if defined(SIMDBEST) && defined(MULTITHREAD) 
    uint32_t num_threads = min(8, K);
    pthread_t threads[num_threads];
    multiply_matrix_data_t thread_data[num_threads];

    uint32_t rows_per_thread = K / num_threads;
    for (uint32_t t = 0; t < num_threads; t++) {
        thread_data[t].matrix1 = matrix1;
        thread_data[t].matrix2 = matrix2;
        thread_data[t].result = result;
        thread_data[t].K = K;
        thread_data[t].start_row = t * rows_per_thread;
        thread_data[t].end_row = (t == num_threads - 1) ? K : (t + 1) * rows_per_thread;

        // Create a thread to compute its assigned rows
#if defined(SIMD512) || defined(SIMD256) || defined(SIMD128) || defined(SIMDBEST)
        pthread_create(&threads[t], NULL, multiply_matrix_simd_thread, (void *)&thread_data[t]);
#else 
        pthread_create(&threads[t], NULL, multiply_matrix_thread, (void *)&thread_data[t]);
#endif
    }

    for (uint32_t t = 0; t < num_threads; t++) {
        pthread_join(threads[t], NULL);
    }
#elif defined (BEST)
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
#if defined (BEST) || (defined(UNROLL) && defined(CACHE_AWARE)) 
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

void *test_patterns_thread(void *arg) {
    test_patterns_data_t *data = (test_patterns_data_t *)arg;
    uint32_t *matrix = data->matrix;
    uint32_t matrix_size = data->matrix_size;
    uint32_t *patterns = data->patterns;
    uint32_t pattern_size = data->pattern_size;
    uint32_t *res = data->res;
    uint32_t start_pattern = data->start_pattern;
    uint32_t end_pattern = data->end_pattern;
    const uint32_t m = matrix_size * matrix_size;

    for (uint32_t i = 0; i < m - pattern_size + 1; i++) {
        for (uint32_t j = start_pattern; j < end_pattern; j++) {
            uint32_t dist = 0;
            uint32_t new_j = j * pattern_size;
            uint32_t k = 0;

            __builtin_prefetch(&patterns[new_j], 0, 1);

            for (; k + 4 <= pattern_size; k += 4) {
                uint32_t diff0 = matrix[i + k] - patterns[new_j + k];
                uint32_t diff1 = matrix[i + k + 1] - patterns[new_j + k + 1];
                uint32_t diff2 = matrix[i + k + 2] - patterns[new_j + k + 2];
                uint32_t diff3 = matrix[i + k + 3] - patterns[new_j + k + 3];
                dist += diff0 * diff0 + diff1 * diff1 + diff2 * diff2 + diff3 * diff3;

                __builtin_prefetch(&matrix[i + k + 4], 0, 1);
                __builtin_prefetch(&patterns[new_j + k + 4], 0, 1);
            }

            for (; k < pattern_size; k++) {
                dist += (matrix[i + k] - patterns[new_j + k]) * (matrix[i + k] - patterns[new_j + k]);
            }

            if (dist < res[j]) {
                res[j] = dist;
            }
        }
    }
    return NULL;
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
    
    for (uint32_t i = 0; i < nb_patterns; i++) {
        res[i] = UINT32_MAX;
    }

#if defined(MULTITHREAD) && defined(BEST)
    uint32_t thread_count = min(8, nb_patterns);
    pthread_t threads[thread_count];
    test_patterns_data_t thread_data[thread_count];

    uint32_t patterns_per_thread = nb_patterns / thread_count;
    uint32_t extra_patterns = nb_patterns % thread_count;
    uint32_t start_pattern = 0;
    for (uint32_t t = 0; t < thread_count; t++) {
        uint32_t thread_patterns = patterns_per_thread + (t < extra_patterns ? 1 : 0);

        thread_data[t].matrix = matrix;
        thread_data[t].matrix_size = matrix_size;
        thread_data[t].patterns = patterns;
        thread_data[t].pattern_size = pattern_size;
        thread_data[t].nb_patterns = nb_patterns;
        thread_data[t].res = res;
        thread_data[t].start_pattern = start_pattern;
        thread_data[t].end_pattern = start_pattern + thread_patterns;

        start_pattern += thread_patterns;

        pthread_create(&threads[t], NULL, test_patterns_thread, &thread_data[t]);
    }

    for (uint32_t t = 0; t < thread_count; t++) {
        pthread_join(threads[t], NULL);
    }
#else 
    const uint32_t m = matrix_size * matrix_size;
    for (uint32_t i = 0; i < m - pattern_size + 1; i++) {
        for (uint32_t j = 0; j < nb_patterns; j++) {
            uint32_t dist = 0;
            uint32_t new_j = j * pattern_size;
            uint32_t k = 0;

            __builtin_prefetch(&patterns[new_j], 0, 1);

#if defined(UNROLL)
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
#endif
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
    return res_str;
}