inginious:
	tar --exclude='*.o' --exclude='*.so' -zcvf project.tar.gz project/
build: 
	gcc tests/main.c project/utils/utils.c project/utils/utils.h -o tests/main
	