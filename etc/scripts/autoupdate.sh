#!/bin/bash
#
##   semi-automated script installing FairSoft, uHAL (cactus) and DPB controls
#

# 24.10.2016 - Add TS and Flesnet and adapt to git repo
# 01.03.2016 - initial version from cbmroot autoinstall_framework.sh r.9499
# by Pierre-Alain Loizeau

#-------------------------------------
# Possible options:
# ./autoinstall.sh [gsi] [dev] [ [d [t [F [c]]]] ]
#   with
#     * gsi switching ON the compilation with a newer custom compiler at GSI
#     * dev switching the compiled versions of the osftware to the development ones
#     * dep switching ON the installation/check of dependencies for the chosen software
#       (see f, u and d)
#     * d = 0 or 1 the flag controlling the installation of DPB controls
#     * t = 0 or 1 the flag controlling the installation of TS software
#     * F = 0 or 1 the flag controlling the installation of FLESNET
#     * c = 0 or 1 the flag controlling the installation of FairRoot and CbmRoot
#         (assumes same FairSoft version for pro/dev in CbmRoot autoinstall)
# usage:
# svn co https://subversion.gsi.de/cbmsoft/daq/trunk/config/dpbcontrols $DPBSRCDIR
# cd $DPBSRCDIR
# ./autoinstall.sh dev 1 0 0 0
# or
# ./autoinstall.sh 0 0 1 0
# or
# ./autoinstall.sh 1 1 1 1
#-------------------------------------

# Root version if Fairsoft is installed
export ROOTVER=6

# put your desired variants here:
export FSOFTDEV=may16p1
#export BOOSTDEV=1.57.0 # ONLY in case we don't use FairSoft
export UHALDEV=2_4_2

export FSOFTPRO=nov15p7
#export BOOSTPRO=1.57.0 # ONLY in case we don't use FairSoft
export UHALPRO=2_4_2

# former versions
# fairsoft:
# uhal:

export DEBIANSYST=`uname -a | grep Debian | wc -l`
export NUMOFCPU=`cat /proc/cpuinfo | grep processor | wc -l`
export DPBSRCDIR=`pwd`

#-------------------------------------

# Flag for version check
export ISDEV=0
# set default version to pro
export FSOFTVER=$FSOFTPRO
#export BOOSTVER=$BOOSTPRO # ONLY in case we don't use FairSoft
export UHALVER=$UHALPRO

# Set default NOT to install the software dependencies
INSTALL_DEP=0

# check if we want to run with GSI compiler
if [ $# -ge 1 ]; then
  if [ "$1" == "gsi" ]; then
    # use a different compiler from GSI
    . /usr/share/modules/init/bash
    module use /cvmfs/it.gsi.de/modulefiles/
    module load compiler/gcc/4.9.2
    export CC=gcc
    export FC=gfortran
    export CXX=g++
    shift
  fi
fi

# check if we want to run with dev
if [ $# -ge 1 ]; then
  if [ "$1" == "dev" ]; then
    export ISDEV=1
    export FSOFTVER=$FSOFTDEV
    #    export BOOSTVER=$BOOSTDEV # ONLY in case we don't use FairSoft
    export UHALVER=$UHALDEV
    shift
  fi
fi

# check if we want to run with dependences check
if [ $# -ge 1 ]; then
  if [ "$1" == "dep" ]; then
    INSTALL_DEP=1
    shift
  fi
fi

echo FSOFTVER: $FSOFTVER
echo UHALVER:  $UHALVER

if [ $INSTALL_DEP -ge 1 ]; then
  echo "Install dependencies for all possible software!"
  echo "=> You will be asked for the user/root password ..."
fi

# Update everything by default
SETUP_DPB=1
SETUP_TS=1
SETUP_FLESNET=1
SETUP_CBMROOT=0

echo number of parameters: $#

# handle parameters, if supplied
if [ $# -eq 1 ]; then
  SETUP_DPB=$1
  SETUP_TS=0
  SETUP_FLESNET=0
  SETUP_CBMROOT=0
fi
# handle parameters, if supplied
if [ $# -eq 2 ]; then
  SETUP_DPB=$1
  SETUP_TS=$2
  SETUP_FLESNET=0
  SETUP_CBMROOT=0
fi
# handle parameters, if supplied
if [ $# -eq 3 ]; then
  SETUP_DPB=$1
  SETUP_TS=$2
  SETUP_FLESNET=$3
  SETUP_CBMROOT=0
fi

# handle parameters, if supplied
if [ $# -eq 4 ]; then
  SETUP_DPB=$1
  SETUP_TS=$2
  SETUP_FLESNET=$3
  SETUP_CBMROOT=$4
fi

echo "Update DPB controls:         " $SETUP_DPB
echo "Update TS software:          " $SETUP_TS
echo "Update Flesnet:              " $SETUP_FLESNET
echo "Update FairRoot and CbmRoot: " $SETUP_CBMROOT
echo

if [ $SETUP_FLESNET -ge 1 ]; then
  echo "Checking if sudo allowed, this may generate email to root!"
  sudo -n true
  if [ "$?" == 1 ]; then
    echo "sudo access => root commands execute with sudo"
    SUDO_ROOT=1
  else
    echo "no sudo access => root commands execute through su"
    SUDO_ROOT=0
  fi
else
  SUDO_ROOT=0
fi

# Load the ipbuslogin script, that should be enough for everything except CbmRoot
cd ..
source ipbuslogin.sh

# If option ON, Update and re-Compile DPB controls project
if [ $SETUP_DPB -ge 1 ]; then
  echo "Updating DPB controls ..."

  ## Go to source folder
  cd $DPBSRCDIR

  ## Update the folder
  git pull

  ## Go in build folder
  cd build

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done updating DPB Controls"
fi

# If option ON, Update and Re-Compile TS software
if [ $SETUP_TS -ge 1 ]; then
  echo "Updating TS software ..."

  ## Go to the right folder
  cd $DPBSRCDIR/../ts_systems

  ## Update the folder
  git pull

  ## Go to software source folder
  cd sw/ts_sys_ipbus_sw

  echo "current folder"
  echo `pwd`

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done updating TS software"

fi

# If option ON, Update and Re-Compile FLESNET
if [ $SETUP_FLESNET -ge 1 ]; then
  echo "Updating FLESNET ..."

  ## Update the Flesnet source adpated to DPB by PAL
#  cd $DPBSRCDIR/../flesnet_pal
  cd $DPBSRCDIR/../flesnet
  git pull

  ## if not simpath and FairsoftPath, copy into simpath
  if [ ! -z "$FAIRSOFTPATH" ] && [ -z "$SIMPATH" ]; then
    export SIMPATH=$FAIRSOFTPATH
  fi

  ## install PDA !!root access needed!!
  cd contrib/
  echo "Installing FLESNET PDA "

  if [ $SUDO_ROOT -ge 1 ]; then
    echo "Installing with sudo => user password, single use"
    sudo -k ./pda_inst.sh
  else
    echo "Installing with su => root password, single use"
    su -c "pwd;./pda_inst.sh"
  fi
  cd ..

  ## Go to build folder
  cd build

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done Updating FLESNET"
fi

# If option ON, Update and Re-Compile CbmRoot
if [ $SETUP_CBMROOT -ge 1 ]; then
  echo "Updating CbmRoot ..."

  ## Update the CbmRoot source including the autoinstall script
  cd $DPBSRCDIR/../cbmroot_trunk
  svn up

  echo "current folder"
  echo `pwd`

  ## Go to build folder and load config script
  cd build
  source config.sh
  
  ## Re-compile CbmRoot
  nice make -j$NUMOFCPU

  echo "done Updating CBMROOT"
fi
