build: main.c ../project/utils/utils.c
	mkdir -p build 
	gcc -o build/main main.c ../project/utils/utils.c -I../project/utils -Wall -Wextra -Werror -std=c99 -pedantic -g
run: build
	./build/main
