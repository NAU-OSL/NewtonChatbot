FROM gitpod/workspace-full:latest

USER root
RUN apt-get update && apt-get install -y \
  cloc graphviz \
  && apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*
  
USER gitpod

RUN wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
RUN bash Anaconda3-2022.05-Linux-x86_64.sh -b
RUN rm Anaconda3-2022.05-Linux-x86_64.sh
ENV PATH=$PATH:$HOME/anaconda3
ENV PATH=$PATH:$HOME/anaconda3/bin
RUN conda install conda
RUN ["/bin/bash", "-c", ". /home/gitpod/anaconda3/etc/profile.d/conda.sh && conda create -n newton -c conda-forge python=3.9 jupyterlab=3 matplotlib seaborn lightgbm catboost -y"]
RUN conda init
ENV jupynb="jupyter notebook --NotebookApp.allow_origin=\'$(gp url 8888)\' --ip='*' --NotebookApp.token='' --NotebookApp.password=''"
ENV jupylab="jupyter lab --NotebookApp.allow_origin=\'$(gp url 8888)\' --ip='*' --NotebookApp.token='' --NotebookApp.password='' --collaborative"

USER root
