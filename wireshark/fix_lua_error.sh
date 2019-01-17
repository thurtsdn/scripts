#!/bin/bash

sudo sed -i 's/dofile(DATA_DIR.."console.lua")/--dofile(DATA_DIR.."console.lua")/' /usr/local/share/wireshark/init.lua
