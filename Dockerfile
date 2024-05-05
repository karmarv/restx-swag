FROM ubuntu:jammy

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
	python3-opencv ca-certificates python3-dev git wget sudo ninja-build vim
RUN ln -sv /usr/bin/python3 /usr/bin/python

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} rv -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER rv
WORKDIR /home/rv

ENV PATH="/home/rv/.local/bin:${PATH}"
RUN wget https://bootstrap.pypa.io/pip/3.6/get-pip.py && \
	python3 get-pip.py --user && \
	rm get-pip.py


#This command will copy the dependancies and libaries in the requirements.txt to the working directory
RUN git clone https://github.com/karmarv/restx-swag.git
RUN cd restx-swag && pip install -r requirements.txt --no-cache-dir

CMD cd restx-swag && deploy_api.bash