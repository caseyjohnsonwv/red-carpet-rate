FROM python:3.8-slim-buster

# set up virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR ${VIRTUAL_ENV}

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

# install and run the main script
COPY main.py ./main.py
CMD [ "python3", "main.py" ]
