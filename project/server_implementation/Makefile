CFLAGS= -ggdb -fPIC -Wextra -Werror -Wall -pedantic
build: main.c ../utils/utils.c
	gcc -I../../nginx-link-function/src -I ../utils -c $(CFLAGS) main.c -o build/main.o -lm
	gcc -I../utils -c $(CFLAGS) ../utils/utils.c -o build/utils.o -lm
	gcc -shared $(CFLAGS) -o build/libmain.so build/main.o build/utils.o -lm
clean:
	rm -f build/*.o build/*.so
kill_nginx:
	@echo "Killing previous NGINX instances..."
	@##Ignore the error if there is no nginx instances running
	@pkill nginx || echo "No previous NGINX instances was running..."

run_release: build kill_nginx
	@echo "Application is running in release mode, this is the prefered mode for measurements..."
	../../nginx/install_release/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;";

run_debug: build kill_nginx
	@echo "Application is running in debug mode, this is the prefered mode for development..."
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
	@echo "Application is running in valgrind mode, this is an handy debug tool..."
	valgrind ../../nginx/install_debug/sbin/nginx -c ../../project/nginx-conf/project.conf -g "error_log /dev/stdout error; daemon off;";

