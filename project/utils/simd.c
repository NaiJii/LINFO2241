#include "simd.h"
#include "utils.h"

void* multiply_matrix_simd_thread(void *arg) {
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

#if defined(SIMD512) || defined(SIMDBEST)
                        __m512i a_vec = _mm512_set1_epi32(a_val); 
                        for (uint32_t j = 0; j < BLOCK_SIZE && (jBlock + j) < K; j += 16) {
                            if (j + 15 < BLOCK_SIZE && jBlock + j + 15 < K) {
                                __builtin_prefetch(&b_ptr[j + 16], 0, 1);

#if defined(ALIGNED)
                                __m512i b_vec = _mm512_load_si512((__m512i *)&b_ptr[j]);
                                __m512i r_vec = _mm512_load_si512((__m512i *)&r_ptr[j]);
#else
                                __m512i b_vec = _mm512_loadu_si512((__m512i *)&b_ptr[j]);
                                __m512i r_vec = _mm512_loadu_si512((__m512i *)&r_ptr[j]);
#endif
                                
                                __m512i prod_vec = _mm512_mullo_epi32(a_vec, b_vec);        
                                r_vec = _mm512_add_epi32(r_vec, prod_vec);                  
                                
#if defined(ALIGNED)
                                _mm512_store_si512((__m512i *)&r_ptr[j], r_vec);
#else
                                _mm512_storeu_si512((__m512i *)&r_ptr[j], r_vec);
#endif
                            } else {
                                for (uint32_t jj = 0; jj < 16 && jBlock + j + jj < K; jj++) {
                                    r_ptr[j + jj] += a_val * b_ptr[j + jj];
                                }
                            }
                        }
#elif defined(SIMD256)
                        __m256i a_vec = _mm256_set1_epi32(a_val); 
                        for (uint32_t j = 0; j < BLOCK_SIZE && (jBlock + j) < K; j += 8) {
                            if (j + 7 < BLOCK_SIZE && jBlock + j + 7 < K) {
                                __builtin_prefetch(&b_ptr[j + 8], 0, 1);

#if defined(ALIGNED)
                                __m256i b_vec = _mm256_load_si256((__m256i *)&b_ptr[j]);
                                __m256i r_vec = _mm256_load_si256((__m256i *)&r_ptr[j]);
#else
                                __m256i b_vec = _mm256_loadu_si256((__m256i *)&b_ptr[j]);
                                __m256i r_vec = _mm256_loadu_si256((__m256i *)&r_ptr[j]);
#endif
                                
                                __m256i prod_vec = _mm256_mullo_epi32(a_vec, b_vec);    
                                r_vec = _mm256_add_epi32(r_vec, prod_vec);
                                
#if defined(ALIGNED)
                                _mm256_store_si256((__m256i *)&r_ptr[j], r_vec);
#else
                                _mm256_storeu_si256((__m256i *)&r_ptr[j], r_vec);
#endif
                            } else {
                                for (uint32_t jj = 0; jj < 8 && jBlock + j + jj < K; jj++) {
                                    r_ptr[j + jj] += a_val * b_ptr[j + jj];
                                }
                            }
                        }
#elif defined(SIMD128)
                        __m128i a_vec = _mm_set1_epi32(a_val); 
                        for (uint32_t j = 0; j < BLOCK_SIZE && (jBlock + j) < K; j += 4) {
                            if (j + 3 < BLOCK_SIZE && jBlock + j + 3 < K) {
                                __builtin_prefetch(&b_ptr[j + 4], 0, 1);

#if defined(ALIGNED)
                                __m128i b_vec = _mm_load_si128((__m128i *)&b_ptr[j]);
                                __m128i r_vec = _mm_load_si128((__m128i *)&r_ptr[j]);
#else
                                __m128i b_vec = _mm_loadu_si128((__m128i *)&b_ptr[j]);
                                __m128i r_vec = _mm_loadu_si128((__m128i *)&r_ptr[j]);
#endif
                                
                                __m128i prod_vec = _mm_mullo_epi32(a_vec, b_vec);
                                r_vec = _mm_add_epi32(r_vec, prod_vec);    
                                
#if defined(ALIGNED)
                                _mm_store_si128((__m128i *)&r_ptr[j], r_vec);
#else
                                _mm_storeu_si128((__m128i *)&r_ptr[j], r_vec);
#endif
                            } else {
                                for (uint32_t jj = 0; jj < 4 && jBlock + j + jj < K; jj++) {
                                    r_ptr[j + jj] += a_val * b_ptr[j + jj];
                                }
                            }
                        }
#elif SIMD
#error "You're missing a define for SIMD instructions"
#endif
                    }
                }
            }
        }
    }
    return NULL;
}
