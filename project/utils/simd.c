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

    for (uint32_t i = start_row; i < end_row; i++) {
        for (uint32_t k = 0; k < K; k++) {
#if defined(SIMD512)
            __m512i a_vec = _mm512_set1_epi32(matrix1[i * K + k]);
            uint32_t j = 0;
            for (; j + 16 <= K; j += 16) {
                __m512i b_vec = _mm512_loadu_si512((__m512i *)&matrix2[k * K + j]);
                __m512i r_vec = _mm512_loadu_si512((__m512i *)&result[i * K + j]);
                __m512i prod_vec = _mm512_mullo_epi32(a_vec, b_vec);
                r_vec = _mm512_add_epi32(r_vec, prod_vec);
                _mm512_storeu_si512((__m512i *)&result[i * K + j], r_vec);
            }
            for (; j < K; j++) {
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
            }
#elif defined(SIMD256) || defined(SIMDBEST) 
            __m256i a_vec = _mm256_set1_epi32(matrix1[i * K + k]);
            uint32_t j = 0;
            for (; j + 8 <= K; j += 8) {
                __m256i b_vec = _mm256_loadu_si256((__m256i *)&matrix2[k * K + j]);
                __m256i r_vec = _mm256_loadu_si256((__m256i *)&result[i * K + j]);
                __m256i prod_vec = _mm256_mullo_epi32(a_vec, b_vec);
                r_vec = _mm256_add_epi32(r_vec, prod_vec);
                _mm256_storeu_si256((__m256i *)&result[i * K + j], r_vec);
            }
            for (; j < K; j++) {
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
            }
#elif defined(SIMD128)
            __m128i a_vec = _mm_set1_epi32(matrix1[i * K + k]);
            uint32_t j = 0;
            for (; j + 4 <= K; j += 4) {
                __m128i b_vec = _mm_loadu_si128((__m128i *)&matrix2[k * K + j]);
                __m128i r_vec = _mm_loadu_si128((__m128i *)&result[i * K + j]);
                __m128i prod_vec = _mm_mullo_epi32(a_vec, b_vec);
                r_vec = _mm_add_epi32(r_vec, prod_vec);
                _mm_storeu_si128((__m128i *)&result[i * K + j], r_vec);
            }
            for (; j < K; j++) {
                result[i * K + j] += matrix1[i * K + k] * matrix2[k * K + j];
            }
#elif SIMD
#error "You're missing a define for SIMD instructions"
#endif
        }
    }
    return NULL;
}
