#!/usr/bin/env bash
source /opt/ipbus-software/uhal/tests/setup.sh
cd /opt/epics/sca_lib_py && rm entrypoint.sh && git pull
./sca_srv.py