FROM python:3.10-buster

RUN apt-get -y update

# install google chrome

# COPY ./google-chrome-stable_current_amd64.deb ./
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# Install the Chrome Debian package
RUN apt install ./google-chrome-stable_current_amd64.deb -y

# install chromedriver
COPY ./chromedriver /usr/local/bin/

# set display port to avoid crash

ENV DISPLAY=:99

# install selenium

RUN pip install selenium==4.22.0
RUN pip install fastapi pandas requests uvicorn webdriver_manager selenium beautifulsoup4 html5lib lxml openpyxl
WORKDIR /app
COPY . /app

EXPOSE 8000

# CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000","--reload"]