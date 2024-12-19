#include <math.h>
#include <ngx_link_func_module.h>
// #include <ngx_core.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "utils.h"
#if defined SIMD
#include "simd.h"
#elif defined SIMT
#include <cuda_runtime.h>
#include "simt.h"
#endif


int is_service_on = 0;

/**
 * @brief Process the request's body, and return a response. This is the
 * function you should implement.
 *
 * @param ctx The context of the request, only used for logging and memory
 * allocation.
 * @param body The request's body, as a string.
 * @param body_len The length of the request's body.
 * @param resp_len The length of the response.
 *
 * @note You will do the required operations based on the request's body, and
 * return a response. BE CAREFUL, you MUST store the length of your response in
 * `resp_len` before returning.
 *
 * @note Also, this environment keeps you from doing classical `malloc` to
 * allocate memory. Instead, use the function `ngx_link_func_palloc(ctx,
 * number_of_bytes)`. You can also use `ngx_link_func_pcalloc(ctx, number_of_bytes)` 
 * instead of `calloc`. The advantage of this method is that your memory
 * allocation is linked to the request and everything is freed when the resquest
 * finished. No need to worry about freeing memory :)
 */

static char *body_processing(ngx_link_func_ctx_t *ctx, char *body, size_t body_len,
                             size_t *resp_len) {

    struct parsed_request parsed;
    parse_request(&parsed, body, body_len);

    char* res_str = ngx_link_func_palloc(ctx, (10 * parsed.nb_patterns + 1) * sizeof(char));
    uint32_t* res_uint = NULL;
    uint32_t* intermediary_matrix = NULL;

    if (parsed.matrices_size <= 0) {
        res_uint = (uint32_t*)alloca(parsed.nb_patterns * sizeof(uint32_t));
        intermediary_matrix = (uint32_t*)alloca(parsed.matrices_size * parsed.matrices_size * sizeof(uint32_t));
    }   
    else {
        res_uint = ngx_link_func_palloc(ctx, parsed.nb_patterns * sizeof(uint32_t));
        intermediary_matrix = ngx_link_func_palloc(ctx, parsed.matrices_size * parsed.matrices_size * sizeof(uint32_t));
    }

    if (res_uint == NULL || intermediary_matrix == NULL) {
        return NULL;
    }

    multiply_matrix(parsed.mat1, parsed.mat2, intermediary_matrix, parsed.matrices_size);

    test_patterns(intermediary_matrix, parsed.matrices_size, parsed.patterns,parsed.patterns_size, parsed.nb_patterns, res_uint);

    res_to_string(res_str, res_uint, parsed.nb_patterns);
    
    *resp_len = strlen(res_str);
    PRINTF("resp %s\n", res_str);

    return res_str;
}

void main_function(ngx_link_func_ctx_t *ctx) {
    // Retrieve request's body
    char *body = (char *)ctx->req_body;
    size_t body_len = ctx->req_body_len;

    // Process the request's body
    size_t resp_len = 0;
    char *resp = body_processing(ctx, body, body_len, &resp_len);
    // Warn user in case of error during processing
    if (resp == NULL) {
        ngx_link_func_write_resp(ctx, 500, "500 Internal Server Error", "text/plain",
                                 "Failed to parse request's body",
                                 sizeof("Failed to parse request's body") - 1);
        return;
    }
    // Warn user if he forgot to set the response's length
    if (resp_len == 0) {
        ngx_link_func_write_resp(ctx, 500, "500 Internal Server Error", "text/plain",
                                 "You forgot to set the response's length ! :angry:",
                                 sizeof("You forgot to set the response's length ! :angry:") - 1);
        return;
    }
    // Return the response
    ngx_link_func_write_resp(ctx, 200, "200 OK", "text/plain", resp, resp_len);
}

/**
 * A function that is called when the application is started.
 *
 * You shouldn't do anything here
 */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
void ngx_link_func_init_cycle(ngx_link_func_cycle_t *cycle) {
    ngx_link_func_cyc_log(info, cycle, "%s", "Starting application, new logs !");
    is_service_on = 1;
#ifdef SIMT
    cudaError_t err;
    //err = cudaInitDevice(0, 0, 0);
    err = cudaSuccess;
    if (err != cudaSuccess) printf("Error while initializing CUDA in cudaInitDevice: %s\n", cudaGetErrorString(err));
    err = cudaSetDevice(0);
    if (err != cudaSuccess) printf("Error while initializing CUDA in cudaSetDevice: %s\n", cudaGetErrorString(err));
#endif

}

/**
 * A function that is called when the application is stopped.
 *
 * You shouldn't do anything here
 */
void ngx_link_func_exit_cycle(ngx_link_func_cycle_t *cyc) {
    ngx_link_func_cyc_log(info, cyc, "%s\n", "Shutting down/reloading the Application");
    is_service_on = 0;
}
#pragma GCC diagnostic pop
