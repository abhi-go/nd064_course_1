FROM python:2.7
MAINTAINER Abhinav Goyal "ag@abhinavgoyal.info"

# Copy files to the target
COPY techtrends /app
WORKDIR /app

# run python installation to get libraries
RUN pip install -r requirements.txt
# initialize sqlite db
RUN python init_db.py
COPY . /app

# expose the port for flask to listen on
EXPOSE 3111

# RUN the app
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
