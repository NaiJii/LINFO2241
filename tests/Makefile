P3_FLAGS = -mno-sse2 -mno-avx -mno-avx2 -mno-avx512f -fno-unroll-loops -fno-tree-vectorize -O2 
override CFLAGS+= -ggdb -fPIC -Wextra -Werror -Wall -pedantic $(P3_FLAGS)
NB_WORKER = 1

CACHE_AWARE_FLAG = $(findstring -DCACHE_AWARE,$(CFLAGS))
UNROLL_FLAG = $(findstring -DUNROLL,$(CFLAGS))
BEST_FLAG = $(findstring -DBEST,$(CFLAGS))
NGX_FLAG = $(findstring -DNGX,$(CFLAGS))


CACHE_AWARE_FLAG = $(findstring -DCACHE_AWARE,$(CFLAGS))
UNROLL_FLAG = $(findstring -DUNROLL,$(CFLAGS))
BEST_FLAG = $(findstring -DBEST,$(CFLAGS))
NGX_FLAG = $(findstring -DNGX,$(CFLAGS))

.PHONY: check-flags
check-flags:
ifeq ($(CACHE_AWARE_FLAG),-DCACHE_AWARE)
	@echo "CFLAGS contains -DCACHE_AWARE"
else
	@echo "CFLAGS does not contain -DCACHE_AWARE"
endif

ifeq ($(UNROLL_FLAG),-DUNROLL)
	@echo "CFLAGS contains -DUNROLL"
else
	@echo "CFLAGS does not contain -DUNROLL"
endif
	
ifeq ($(BEST_FLAG),-DBEST)
	@echo "CFLAGS contains -DBEST"
else
	@echo "CFLAGS does not contain -DBEST"
endif

ifeq ($(NGX_FLAG),-DNGX)
	@echo "CFLAGS contains -DNGX"
else
	@echo "CFLAGS does not contain -DNGX"
endif 

build: check-flags main.c ../project/utils/utils.c
	mkdir -p build 
	gcc ../project/utils/utils.c -I../project/utils $(CFLAGS) main.c -o build/main.o -lm -std=c99 -g -D_POSIX_C_SOURCE=199309L
run: build
	./build/main

