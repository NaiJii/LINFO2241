#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <math.h>

#ifdef DEBUG
#define PRINTF(str, ...) printf(str, ##__VA_ARGS__)
#else
#define PRINTF(...)
#endif

#define MULTITHREAD

// Blocking size 
#if defined (SIMD512) || defined (SIMDBEST) 
#define BLOCK_SIZE 16
#elif defined (SIMD256)
#define BLOCK_SIZE 8
#elif defined (SIMD128)
#define BLOCK_SIZE 4
#else
#define BLOCK_SIZE 8
#endif 

#define min(a, b) (((a)<(b))?(a):(b))

struct parsed_request {
    // the size of the key
    uint32_t matrices_size;
    // First matrix
    uint32_t *mat1;
    // Second matrix
    uint32_t *mat2;
    // The number of patterns
    uint32_t nb_patterns;
    // The size of the patterns
    uint32_t patterns_size;
    // The patterns to match
    uint32_t *patterns;
};

typedef struct {
    uint32_t *matrix1;
    uint32_t *matrix2;
    uint32_t *result;
    uint32_t K;
    uint32_t start_row;
    uint32_t end_row;
} multiply_matrix_data_t;

typedef struct {
    uint32_t *matrix;
    uint32_t matrix_size;
    uint32_t *patterns;
    uint32_t pattern_size;
    uint32_t nb_patterns;
    uint32_t *res;
    uint32_t start_pattern;
    uint32_t end_pattern;
} test_patterns_data_t;

int foo(void);
// Functions you are asked to implement
void parse_request(struct parsed_request *parsed, char *request, size_t request_len);
void multiply_matrix(uint32_t *matrix1, uint32_t *matrix2, uint32_t *result, uint32_t K);
void test_patterns(uint32_t *matrix, uint32_t matrix_size, uint32_t *patterns,
                      uint32_t pattern_size, uint32_t nb_patterns, uint32_t *res);
void res_to_string(char *str, uint32_t *res, uint32_t res_size);
char *complete_algorithm(char *raw_request, uint32_t raw_request_len, char *res_str, uint32_t *res_uint, uint32_t *intermediary_matrix, uint32_t *resp_len);
uint32_t extract_number(char **str);

// Multithreaded functions
void *multiply_matrix_thread(void *arg);
void *test_patterns_thread(void *arg);

uint64_t checksum(uint8_t* data, size_t len);
uint64_t checksum_request(struct parsed_request* request);

// map that matches request checksum (uint64_t) to the response (char*)
extern uint64_t last_request;
extern char* last_response;