#!/bin/bash

# Convenience script to build snap and our project (C++ flavor).

# Build snap
cd Snap-2.3
make -j 2 all

cd ..
