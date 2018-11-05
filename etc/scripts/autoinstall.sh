#!/bin/bash
#
##   semi-automated script installing FairSoft, uHAL (cactus) and DPB controls
#

# 24.10.2016 - Add TS and Flesnet and adapt to git repo
# 01.03.2016 - initial version from cbmroot autoinstall_framework.sh r.9499
# by Pierre-Alain Loizeau

#-------------------------------------
# Possible options:
# ./autoinstall.sh [gsi] [dev] [dep] [f [u [d [t [F [c]]]]]]
#   with
#     * gsi switching ON the compilation with a newer custom compiler at GSI
#     * dev switching the compiled versions of the osftware to the development ones
#     * dep switching ON the installation/check of dependencies for the chosen software
#       (see f, u and d)
#     * f = 0 or 1 the flag controlling the installation of Fairsoft
#     * u = 0 or 1 the flag controlling the installation of uHAL
#     * d = 0 or 1 the flag controlling the installation of DPB controls
#     * t = 0 or 1 the flag controlling the installation of TS software
#     * F = 0 or 1 the flag controlling the installation of FLESNET
#     * c = 0 or 1 the flag controlling the installation of FairRoot and CbmRoot
#         (assumes same FairSoft version for pro/dev in CbmRoot autoinstall)
# usage:
# svn co https://subversion.gsi.de/cbmsoft/daq/trunk/config/dpbcontrols $DPBSRCDIR
# cd $DPBSRCDIR
# ./autoinstall.sh dep 0 0 0 0 0 0
# or
# ./autoinstall.sh 0 0 1 0 0 0
# or
# ./autoinstall.sh 1 1 1 1 1 1
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

WRITE_LOGIN=1
# Start filling the login script if option is ON
if [ $WRITE_LOGIN -ge 1 ]; then
  cd ..
  export DAQSOFT_PATH=`pwd`
  rm $DAQSOFT_PATH/ipbuslogin.sh
cat << EndOfInputGen >> $DAQSOFT_PATH/ipbuslogin.sh
export DAQSOFT_PATH=`pwd`
EndOfInputGen
  cd $DPBSRCDIR
fi

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

# install everything by default
SETUP_FAIRSOFT=1
SETUP_UHAL=1
SETUP_DPB=1
SETUP_TS=1
SETUP_FLESNET=1
SETUP_CBMROOT=0

echo number of parameters: $#

# handle parameters, if supplied
if [ $# -eq 1 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=0
  SETUP_DPB=0
  SETUP_TS=0
  SETUP_FLESNET=0
fi
# handle parameters, if supplied
if [ $# -eq 2 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=$2
  SETUP_DPB=0
  SETUP_TS=0
  SETUP_FLESNET=0
fi
# handle parameters, if supplied
if [ $# -eq 3 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=$2
  SETUP_DPB=$3
  SETUP_TS=0
  SETUP_FLESNET=0
fi

# handle parameters, if supplied
if [ $# -eq 4 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=$2
  SETUP_DPB=$3
  SETUP_TS=$4
  SETUP_FLESNET=0
fi

# handle parameters, if supplied
if [ $# -eq 5 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=$2
  SETUP_DPB=$3
  SETUP_TS=$4
  SETUP_FLESNET=$5
fi

# handle parameters, if supplied
if [ $# -eq 6 ]; then
  SETUP_FAIRSOFT=$1
  SETUP_UHAL=$2
  SETUP_DPB=$3
  SETUP_TS=$4
  SETUP_FLESNET=$5
  SETUP_CBMROOT=$6
fi

echo "Install Fairsoft:             " $SETUP_FAIRSOFT
echo "Install uHAL:                 " $SETUP_UHAL
echo "Install DPB controls:         " $SETUP_DPB
echo "Install TS software:          " $SETUP_TS
echo "Install Flesnet:              " $SETUP_FLESNET
echo "Install FairRoot and CbmRoot: " $SETUP_CBMROOT
echo

if [ $INSTALL_DEP -ge 1 ] || [ $SETUP_FLESNET -ge 1 ]; then
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

# If option there, check for general dependencies
if [ $INSTALL_DEP -ge 1 ]; then
  if [ $SUDO_ROOT -ge 1 ]; then
    echo "Installing dependencies with sudo => user password, single use"
    sudo -k apt-get install subversion git build-essential make cmake g++ patch \
        cmake-data gcc gfortran \
        sed libx11-dev libxft-dev \
        libxext-dev libxpm-dev libxmu-dev libglu1-mesa-dev \
        libgl1-mesa-dev ncurses-dev curl bzip2 gzip unzip tar \
        xutils-dev flex bison lsb-release \
        python-dev libc6-dev-i386 libxml2-dev wget libssl-dev \
        libcurl4-openssl-dev automake autoconf libtool \
        libbz2-dev zlib1g-dev ncurses-dev python-dev curl libcurl4-openssl-dev graphviz \
        graphviz-dev uuid-dev libqt4-dev python-qt4 python-qt4-dev python-wxgtk3.0-dev libwxgtk3.0-dev \
        libgd2-xpm-dev libssl-dev \
        libreadline-dev \
        valgrind doxygen libnuma-dev librdmacm-dev libibverbs-dev libkrb5-dev
  else
    echo "Installing dependencies with su => root password, single use"
    su - root -c "apt-get install subversion git build-essential make cmake g++ patch \
        cmake-data gcc gfortran \
        sed libx11-dev libxft-dev \
        libxext-dev libxpm-dev libxmu-dev libglu1-mesa-dev \
        libgl1-mesa-dev ncurses-dev curl bzip2 gzip unzip tar \
        xutils-dev flex bison lsb-release \
        python-dev libc6-dev-i386 libxml2-dev wget libssl-dev \
        libcurl4-openssl-dev automake autoconf libtool \
        libbz2-dev zlib1g-dev ncurses-dev python-dev curl libcurl4-openssl-dev graphviz \
        graphviz-dev uuid-dev libqt4-dev python-qt4 python-qt4-dev python-wxgtk3.0-dev libwxgtk3.0-dev \
        libgd2-xpm-dev libssl-dev \
        libreadline-dev \
        valgrind doxygen libnuma-dev librdmacm-dev libibverbs-dev libkrb5-dev"
  fi
fi

# If option ON, first compile Fairsoft to get Boost and Root
if [ $SETUP_FAIRSOFT -ge 1 ]; then
  echo "Setting up Fairsoft ..."

  ## Download sources
  cd ..
  git clone https://github.com/FairRootGroup/FairSoft fairsoft_src_${FSOFTVER}_root${ROOTVER}
  cd fairsoft_src_${FSOFTVER}_root${ROOTVER}
  git tag -l
  git checkout -b $FSOFTVER $FSOFTVER

  ## Make sure ROOT6 is chosen
  if [ $ROOTVER -eq 6 ]; then
    sed s/build_root6=no/build_root6=yes/ automatic.conf > automatic1_root.conf
  else 
    cp automatic.conf automatic1_root.conf
  fi

  ## If option there, check dependencies
#  if [ $INSTALL_DEP -ge 1 ]; then
#    su - root -c "apt-get install cmake-data gcc gfortran \
#      sed libx11-dev libxft-dev \
#      libxext-dev libxpm-dev libxmu-dev libglu1-mesa-dev \
#      libgl1-mesa-dev ncurses-dev curl bzip2 gzip unzip tar \
#      xutils-dev flex bison lsb-release \
#      python-dev libc6-dev-i386 libxml2-dev wget libssl-dev \
#      libcurl4-openssl-dev automake autoconf libtool \
#      libreadline-dev"
#  fi

  ## Set installation path
  FSOFTINSTALLPATH=`pwd | sed s/fairsoft_src_/fairsoft_/`
  sed /SIMPATH_INSTALL/d automatic1_root.conf > automatic2_path.conf
  echo "  SIMPATH_INSTALL=$FSOFTINSTALLPATH/installation" >> automatic2_path.conf

  ## Use gcc as compiler! (from cbmroot autoinstall, maybe overkill vs Clang?)
  sed s/compiler=/compiler=gcc/ automatic2_path.conf > automatic3_gcc.conf

  ## Depending on option, compile only minimal or standard

  ## If dev, change boost version to one known to work with UHAL IPBUS (downgrade)
  if [ $ISDEV -ge 1 ]; then
    sed -i_ori s/BOOSTVERSION=boost_1_61_0/BOOSTVERSION=boost_1_59_0/ scripts/package_versions.sh
    sed -i s:sourceforge.net/projects/boost/files/boost/1.61.0/:sourceforge.net/projects/boost/files/boost/1.59.0/: scripts/package_versions.sh
  fi

  ## Compile
  ./configure.sh automatic3_gcc.conf

  # Check if the make command succeeded
  case $? in
  42) # Compilation/installation failed !
    echo "FairSoft compilation failed, exiting the autoinstall, please check the errors"
    exit 1
    ;;
  1) # configure script did not recognize the input file
    echo "Input params to FairSoft configure script wrong, check autoinstall script?!?"
    exit 1
    ;;
  0) # FairSoft fully OK
    echo done installing FairSoft
    ;;
  *) # configure script return unknown error
    echo "FairSoft configure script gone wrong, check screen for info?!?"
    exit 1
    ;;
  esac

  ## Save the path to uhal install
  export FAIRSOFTPATH=$FSOFTINSTALLPATH/installation
  export PATH=$FSOFTINSTALLPATH/installation/bin:$PATH

  ## Start filling the login script if option is ON
  if [ $WRITE_LOGIN -ge 1 ]; then
    cat << EndOfInputFS >> $DAQSOFT_PATH/ipbuslogin.sh
export FSOFTVER=${FSOFTVER}
export ROOTVER=${ROOTVER}
EndOfInputFS
    cat << 'EndOfInputFS' >> $DAQSOFT_PATH/ipbuslogin.sh

export FAIRSOFTPATH=$DAQSOFT_PATH/fairsoft_${FSOFTVER}_root${ROOTVER}/installation
export SIMPATH=$FAIRSOFTPATH
export PATH=$FAIRSOFTPATH/bin:$PATH
source $FAIRSOFTPATH/bin/thisroot.sh
export Boost_INCLUDE_DIR=$FAIRSOFTPATH/include/boost
export Boost_LIBRARY_DIR=$FAIRSOFTPATH/lib
EndOfInputFS
  fi


  ## Go back to project source dir
  cd $DPBSRCDIR
fi

# If option ON, compiles UHAL
if [ $SETUP_UHAL -ge 1 ]; then
  echo "Setting up uHAL ..."

  ## If option there, check UHAL dependencies
#  if [ $INSTALL_DEP -ge 1 ]; then
#    su - root -c "apt-get install libbz2-dev zlib1g-dev ncurses-dev python-dev curl libcurl4-openssl-dev graphviz \
#                        graphviz-dev uuid-dev libqt4-dev python-qt4 python-qt4-dev python-wxgtk3.0-dev libwxgtk3.0-dev \
#                        libgd2-xpm-dev libssl-dev"
#  fi

  ## Get UHAL sources
  cd ..
  svn co http://svn.cern.ch/guest/cactus/tags/ipbus_sw/uhal_${UHALVER} uhal_${UHALVER}
  cd uhal_${UHALVER}

  ## Save the path to uhal install
  export UHALPATH=`pwd`
  export CACTUS_ROOT=$UHALPATH/

  ## if simpath and not FairsoftPath, copy into Fairsoftpath
  if [ -z "$FAIRSOFTPATH" ] && [ ! -z "$SIMPATH" ]; then
    export FAIRSOFTPATH=$SIMPATH
  fi

  ## If installing with FairSoft, patch the UHAL config to use  FairSoft BOOST
  if [ ! -z "$FAIRSOFTPATH" ]; then
    echo "Modify uHAL Makefiles to use FairSoft version of boost at "$FAIRSOFTPATH
    ### Change l 32-34 in uhalpath/config/Makefile.macros
    sed -i.bak 's|EXTERN_BOOST_PREFIX = $(CACTUS_RPM_ROOT)/cactuscore/extern/boost/RPMBUILD/SOURCES|EXTERN_BOOST_PREFIX = $(FAIRSOFTPATH)|' $UHALPATH/config/Makefile.macros
    ### Change l3 in main uHAL Makefile to avoid compiling its boost version
    sed -i.bak 's|cactuscore/extern/boost | |' $UHALPATH/Makefile
  else
  ## else download boost 1.57 sources and patch the extern/boost Makefile at l12-15
    echo "Modify uHAL Makefiles to use newer version of boost "
    ### Download and move to right place
    #### First check if file already there and then download
    wget http://downloads.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.bz2
    mv boost_1_57_0.tar.bz2 $UHALPATH/cactuscore/extern/boost/
    ### Patch the makefile to change the version
    sed -i.bak 's/PACKAGE_VER_MINOR = 53/PACKAGE_VER_MINOR = 57/' $UHALPATH/cactuscore/extern/boost/Makefile
  fi

  ## Compile UHAL
  if [ $DEBIANSYST -ge 1 ]; then
    ### if DEBIAN, force it to use bash as shell (otherwise it uses sh which on Debian links to dash)
    echo "DEBIAN systems, typically default shell is not bash => force make to use bash ..."
    make Set=uhal SHELL=/bin/bash
#    make Set=uhal SHELL=/bin/bash -j$NUMOFCPU # NOT working for now as makefile dependencies in uhal not properly done
  else
    ### else standard
    make Set=uhal
#    make Set=uhal -j$NUMOFCPU # NOT working for now as makefile dependencies in uhal not properly done
  fi

  # Check if the make command succeeded
  if [ $? -eq 0 ] ; then
    ## Load UHAL test environment variables (needed for TS soft)
    source $UHALPATH/cactuscore/uhal/tests/setup.sh
    export Boost_INCLUDE_DIR=$FAIRSOFTPATH/include/boost
    export Boost_LIBRARY_DIR=$FAIRSOFTPATH/lib
    export LD_LIBRARY_PATH=$UHALPATH/cactuscore/uhal/tests/lib:$UHALPATH/cactuscore/uhal/uhal/lib:$UHALPATH/cactuscore/uhal/grammars/lib:$UHALPATH/cactuscore/uhal/log/lib:$UHALPATH/cactuscore/extern/pugixml/RPMBUILD/SOURCES/lib:$Boost_LIBRARY_DIR:$LD_LIBRARY_PATH

    ## Start filling the login script if option is ON
    if [ $WRITE_LOGIN -ge 1 ]; then
      cat << EndOfInputUhalA >> $DAQSOFT_PATH/ipbuslogin.sh

export UHALVER=${UHALVER}
EndOfInputUhalA
    cat << 'EndOfInputUhalB' >> $DAQSOFT_PATH/ipbuslogin.sh
export UHALPATH=$DAQSOFT_PATH/uhal_$UHALVER/
export CACTUS_ROOT=$UHALPATH
source $UHALPATH/cactuscore/uhal/tests/setup.sh
export LD_LIBRARY_PATH=$UHALPATH/cactuscore/uhal/tests/lib:$UHALPATH/cactuscore/uhal/uhal/lib:$UHALPATH/cactuscore/uhal/grammars/lib:$UHALPATH/cactuscore/uhal/log/lib:$UHALPATH/cactuscore/extern/pugixml/RPMBUILD/SOURCES/lib:$Boost_LIBRARY_DIR:$LD_LIBRARY_PATH
export ROOT_INCLUDE_PATH="./root/:$UHALPATH/cactuscore/uhal/uhal/include/:$UHALPATH/cactuscore/uhal/uhal/include/TemplateDefinitions:$UHALPATH/cactuscore/uhal/log/include/:$UHALPATH/cactuscore/uhal/grammars/include/:$UHALPATH/cactuscore/uhal/pycohal/include/:$Boost_INCLUDE_DIR"
EndOfInputUhalB
    fi

    echo done installing uHAL
  else
    echo "UHAl compilation failed, exiting the autoinstall, please check the errors"
    exit 1
  fi

  ## Go back to project source dir
  cd $DPBSRCDIR
fi

# If option ON, Compile DPB controls project
if [ $SETUP_DPB -ge 1 ]; then
  echo "Setting up DPB controls ..."

  ## Go to source folder
  cd $DPBSRCDIR

  ## Create build folder
  mkdir build
  cd build

  ## Run cmake
  cmake ..

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done installing DPB Controls"

  ## Printout the configuration info to use the libraries/binaries
#  echo
#  echo ". build/config.sh"
#  echo "export SIMPATH=$SIMPATH"
#  echo "export FAIRROOTPATH=$FAIRROOTPATH"
fi

# If option ON, Download and Compile TS software
if [ $SETUP_TS -ge 1 ]; then
  echo "Setting up TS software ..."

  ## Download the TS source adpated to common install by PAL
  cd $DPBSRCDIR
  cd ..
  git clone git@cbmgsi.githost.io:p.-a.loizeau/ts_systems.git ts_systems

  ## Go to source folder
  cd ts_systems/sw/ts_sys_ipbus_sw

  echo "current folder"
  echo `pwd`

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done installing TS software"

  ## Printout the configuration info to use the libraries/binaries
#  echo
#  echo ". build/config.sh"
#  echo "export SIMPATH=$SIMPATH"
#  echo "export FAIRROOTPATH=$FAIRROOTPATH"
fi

# If option ON, Download and Compile FLESNET
if [ $SETUP_FLESNET -ge 1 ]; then
  echo "Setting up FLESNET ..."

  ## Download the Flesnet source adpated to DPB by PAL
  cd $DPBSRCDIR
  cd ..
#  git clone https://github.com/PALoizeau/flesnet.git flesnet_pal
  git clone https://github.com/cbm-fles/flesnet.git flesnet

  ## Download ZMQ header file not present in newer ZMQ versions
  svn co -r 83 https://github.com/zeromq/cppzmq/trunk cppzmq
  cd cppzmq
  export CPPZMQPATH=`pwd`
  echo "Set CPPZMQPATH to $CPPZMQPATH"
  cd ..

  ## if not simpath and FairsoftPath, copy into simpath
  if [ ! -z "$FAIRSOFTPATH" ] && [ -z "$SIMPATH" ]; then
    export SIMPATH=$FAIRSOFTPATH
  fi

  ## Go to source folder
#  cd flesnet_pal
  cd flesnet

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

  ## Create build folder
  mkdir build
  cd build

  ## Run cmake
  cmake ..

  echo "current folder"
  echo `pwd`

  ## run make (or make install)
  nice make -j$NUMOFCPU

  echo "done installing FLESNET"

  ## Start filling the login script if option is ON
  if [ $WRITE_LOGIN -ge 1 ]; then
    cat << 'EndOfInputFles' >> $DAQSOFT_PATH/ipbuslogin.sh

export CPPZMQPATH=$DAQSOFT_PATH/cppzmq
EndOfInputFles
  fi

  ## Printout the configuration info to use the libraries/binaries
#  echo
#  echo ". build/config.sh"
#  echo "export SIMPATH=$SIMPATH"
#  echo "export FAIRROOTPATH=$FAIRROOTPATH"
fi

# If option ON, Download and Compile FairRoot and CbmRoot
if [ $SETUP_CBMROOT -ge 1 ]; then
  echo "Setting up FairRoot and CbmRoot ..."

  ## Download the CbmRoot source including the autoinstall script
  cd $DPBSRCDIR
  cd ..
  svn co https://subversion.gsi.de/cbmsoft/cbmroot/trunk cbmroot_trunk

  ## Go to source folder
  cd cbmroot_trunk

  echo "current folder"
  echo `pwd`

  ## Make sure we are using ROOT6
  sed 's/#export ROOTVER=6/export ROOTVER=6/' autoinstall_framework.sh > autoinstall_framework.sh_tmp
  sed 's/export ROOTVER=5/#export ROOTVER=5/' autoinstall_framework.sh_tmp > autoinstall_framework.sh
  rm autoinstall_framework.sh_tmp

  ## Call autoinstall script to install pro/dev version of FairRoot
  if [ $ISDEV -ge 1 ]; then
    ./autoinstall_framework.sh dev 0 1 0
  else
    ./autoinstall_framework.sh 0 1 0
  fi

  ## Call autoinstall script to install pro/dev version of CbmRoot
  if [ $ISDEV -ge 1 ]; then
    ./autoinstall_framework.sh dev 0 0 1
  else
    ./autoinstall_framework.sh 0 0 1
  fi
  ## Start filling the login script if option is ON
  if [ $WRITE_LOGIN -ge 1 ]; then
    cat << 'EndOfInputFles' >> $DAQSOFT_PATH/ipbuslogin.sh

alias cbmroot='source $DAQSOFT_PATH/cbmroot_trunk/build/config.sh'
EndOfInputFles
  fi
fi
