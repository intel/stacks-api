FROM python:slim

WORKDIR /usr/src/app

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5055
ENTRYPOINT [ "python3" ]
CMD [ "service.py" ]