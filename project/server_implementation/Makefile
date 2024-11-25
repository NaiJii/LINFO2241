P3_FLAGS = -mno-sse2 -mno-avx -mno-avx2 -mno-avx512f -fno-unroll-loops -fno-tree-vectorize -O2
P4_FLAGS = -mavx2 -mavx512f -msse4 -fno-unroll-loops -fno-tree-vectorize -O2 
override CFLAGS+= -ggdb -fPIC -Wextra -Werror -Wall -pedantic
override NVCCFLAGS+=-O2 -Xcompiler -fPIC,-fno-unroll-loops,-fno-tree-vectorize,-O2

SIMDFLAG=-DSIMD
SIMTFLAG=-DSIMT

CUDA_INCLUDES=-I/usr/local/cuda/include
CUDA_LIBS=-lcudart -L/usr/local/cuda/lib64

NB_WORKER = 1

CACHE_AWARE_FLAG = $(findstring -DCACHE_AWARE,$(CFLAGS))
UNROLL_FLAG = $(findstring -DUNROLL,$(CFLAGS))
BEST_FLAG = $(findstring -DBEST,$(CFLAGS))
OPENMP_FLAG = $(findstring -fopenmp,$(CFLAGS))

.PHONY: check-flags
check-flags:
ifeq ($(CACHE_AWARE_FLAG),-DCACHE_AWARE)
	@echo "CFLAGS contains -DCACHE_AWARE"
endif

ifeq ($(UNROLL_FLAG),-DUNROLL)
	@echo "CFLAGS contains -DUNROLL"
endif
	
ifeq ($(BEST_FLAG),-DBEST)
	@echo "CFLAGS contains -DBEST"
endif

build: main.c ../utils/utils.c check-flags
	gcc -I../../nginx-link-function/src -I ../utils -c $(CFLAGS) $(P3_FLAGS) main.c -o build/main.o -lm
	gcc -I../utils -c $(CFLAGS) ../utils/utils.c -o build/utils.o -lm
	gcc -shared $(CFLAGS) -o build/libmain.so build/main.o build/utils.o -lm

build_simd:
	gcc -I../../nginx-link-function/src -I ../utils -c $(CFLAGS) $(P4_FLAGS) $(SIMDFLAG) main.c -o build/main.o -lm
	gcc -I../utils -c $(CFLAGS) $(P4_FLAGS) $(SIMDFLAG) ../utils/utils.c -o build/utils.o -lm
	gcc -I../utils -c $(CFLAGS) $(P4_FLAGS) $(SIMDFLAG) ../utils/simd.c -o build/simd.o -lm
	gcc -shared $(CFLAGS) $(P4_FLAGS) $(SIMDFLAG) -o build/libmain.so build/main.o build/utils.o build/simd.o -lm

build_simt:
	gcc -I../../nginx-link-function/src -I ../utils $(CUDA_INCLUDES) -c $(CFLAGS) $(P4_FLAGS) $(SIMTFLAG) main.c -o build/main.o -lm $(CUDA_LIBS)
	gcc -I../utils -c $(CFLAGS) $(P4_FLAGS) $(SIMTFLAG) ../utils/utils.c -o build/utils.o -lm $(CUDA_LIBS)
	nvcc -I../utils -c $(NVCCFLAGS) $(SIMTFLAG) ../utils/simt.cu -o build/simt.o -lm $(CUDA_LIBS)
	gcc -shared $(SIMTFLAG) -o build/libmain.so build/utils.o build/simt.o build/main.o -lm $(CUDA_LIBS)

clean:
	rm -f build/*.o build/*.so
kill_nginx:
	echo "Killing previous NGINX instances...\n"
	##Ignore the error if there is no nginx instances running
	pkill nginx || echo "No previous NGINX instances was running...\n"

run_release: build kill_nginx
	echo "Application is running in release mode, this is the prefered mode for measurements..."
	echo "Number of worker: $(NB_WORKER)"
	../../nginx/install_release/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;worker_processes $(NB_WORKER);";

run_release_simd: build_simd kill_nginx
	echo "SIMD optimized application is running in release mode..."
	../../nginx/install_release/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;worker_processes $(NB_WORKER);";

run_release_simt: build_simt kill_nginx
	echo "SIMT optimized application is running in release mode..."
	../../nginx/install_release/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;worker_processes $(NB_WORKER);";

run_debug: build kill_nginx
	echo "Application is running in debug mode, this is the prefered mode for development..."
	../../nginx/install_debug/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;";
	
.SILENT:
run_gdb: build kill_nginx
	echo "Starting NGINX with GDB..."
	NGINX_BIN="../../nginx/install_debug/sbin/nginx";\
	NGINX_CONF="../../project/nginx-conf/project.conf";\
	$${NGINX_BIN} -c $${NGINX_CONF} -g "error_log /dev/stdout error; daemon on;" ;\
	sleep 1 ;\
	NGINX_WORKER_PID=$$(pgrep -f "nginx: worker process" | head -n 1);\
	if [ -z "$$NGINX_WORKER_PID" ]; then\
		echo "Failed to find an nginx worker process. Exiting..." ;\
		exit 1 ;\
	fi;\
	echo "Found nginx worker process with PID: $$NGINX_WORKER_PID";\
	echo "Attaching GDB to nginx worker process $$NGINX_WORKER_PID..." ;\
	gdb -ex "continue" -p $$NGINX_WORKER_PID

run_valgrind: build kill_nginx
	echo "Application is running in valgrind mode, this is a handy debug tool..."
	valgrind ../../nginx/install_debug/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;";

run_valgrind_leak: build kill_nginx
	echo "Application is running in valgrind mode, this is a handy debug tool..."
	valgrind --leak-check=full ../../nginx/install_debug/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;";

