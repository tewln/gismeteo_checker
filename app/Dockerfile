FROM python:3.12

COPY . .

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

RUN chmod 744 /start_bot.sh
CMD ["/start_bot.sh"]