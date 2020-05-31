FROM habrade/epics-base:latest

# Install dependencies for IPbus
RUN apt-get update && apt-get install -y \
    git \
    erlang \
    libboost-all-dev \
    libpugixml-dev \
    python-all-dev \
    python-pip

# Copy built IPbus from container
COPY --from=habrade/ipbus-software:latest /opt/ipbus-software /opt/ipbus-software

# Build and run IOC
ENV sdong_gitlab_token=9Hijhqyyv6bXQ_Ka_YUM
RUN git clone https://sdong:${sdong_gitlab_token}@git.cbm.gsi.de/s.dong/sca_lib_py.git

WORKDIR sca_lib_py
RUN pip install -r requirements.txt

RUN ["/bin/bash", "-c", "source /opt/ipbus-software/uhal/tests/setup.sh"]

#ENTRYPOINT [ "./sca_srv.py" ]