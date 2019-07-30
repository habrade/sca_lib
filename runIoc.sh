#!/usr/bin/env bash
source ../setEnv.sh

afck_num=66
link=1
PREFIX=labtest:Gdpb:$afck_num:SCA:$link

softIocPVA -m P=$PREFIX -d sca.db
