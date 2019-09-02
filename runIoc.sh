#!/usr/bin/env bash
source ../setEnv.sh

afck_num=67
link=0
PREFIX=labtest:Gdpb:$afck_num:SCA:$link

softIocPVA -m P=$PREFIX -d sca.db
