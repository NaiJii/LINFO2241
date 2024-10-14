#include <math.h>
#include <ngx_link_func_module.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "utils.h"

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

    char* res_str = ngx_link_func_palloc(ctx, 65536);
    uint32_t* res_uint = ngx_link_func_palloc(ctx, 1024);
    uint32_t* intermediary_matrix = ngx_link_func_palloc(ctx, 1024);

    //printf("Request: %s\n", body);

    uint32_t resp_len_uint = 0;
    complete_algorithm(body, body_len, res_str, res_uint, intermediary_matrix, &resp_len_uint);
    *resp_len = resp_len_uint;
    //!!!WARNING!!! : In your implementation of the actual server the arrays above should be dynamically allocated using ngx_link_func_palloc/ngx_link_func_pcalloc
    //printf("Response: %s\n", res_str);
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
