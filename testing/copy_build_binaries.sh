#!/bin/bash
BW_PATH=$1
BW_INSTALL_DIR=$2
PLATFORM=$3
CI_TEST_PATH=$4
BW_INTERMEDIATE_DIR=$5

BW_BIN_SRC=$BW_INSTALL_DIR/game/bin/server/$PLATFORM

CI_TEST_DEST=$CI_TEST_PATH/bin/server/$PLATFORM

# Clean up destination
rm -rf $CI_TEST_DEST/server/*
rm -rf $CI_TEST_DEST/tools/*
rm -rf $CI_TEST_DEST/third_party/*
rm -rf $CI_TEST_PATH/res/bigworld

#re-create dir structure
mkdir -p $CI_TEST_DEST/server
mkdir -p $CI_TEST_DEST/tools
mkdir -p $CI_TEST_DEST/third_party
mkdir -p $CI_TEST_PATH/res/bigworld

# Copy artifacts
rsync -r --copy-links $BW_BIN_SRC/server/* $CI_TEST_DEST/server/
rsync -r --copy-links $BW_BIN_SRC/tools/* $CI_TEST_DEST/tools/
rsync -r --copy-links $BW_BIN_SRC/third_party/* $CI_TEST_DEST/third_party/
rsync -r --copy-links $BW_PATH/res/bigworld $CI_TEST_PATH/res
rsync -r --copy-links $BW_INSTALL_DIR/game/res/bigworld $CI_TEST_PATH/res/
