#!/usr/bin/env bash

# Export the project path
export PROJECT_PATH=$PWD
# Downloading NGINX
wget https://nginx.org/download/nginx-1.23.0.tar.gz
tar -xzf nginx-1.23.0.tar.gz
rm nginx-1.23.0.tar.gz
mv nginx-1.23.0/ nginx/
# Download required extension
git clone https://github.com/Taymindis/nginx-link-function.git
# You should include the nginx-link-function header into the c include path
export C_INCLUDE_PATH=$PROJECT_PATH/nginx-link-function/src
# Compile nginx
cd nginx
# NGINX will be installed here, we will have two versions, one for debug and one for performance
mkdir install_release
mkdir install_debug
./configure --add-module=$PROJECT_PATH/nginx-link-function --prefix=$PROJECT_PATH/nginx/install_release
make
make install
./configure --add-module=$PROJECT_PATH/nginx-link-function --prefix=$PROJECT_PATH/nginx/install_debug --with-debug
make
make install

# Adding log files
touch $PROJECT_PATH/nginx/install_release/logs/error.log
touch $PROJECT_PATH/nginx/install_debug/logs/error.log
cd $PROJECT_PATH/project/server_implementation
mkdir build
make -B build
