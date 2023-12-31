FROM python:3.11-slim as builder

RUN apt update && apt upgrade -y && apt install -y gcc g++ build-essential pkg-config
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


FROM builder

WORKDIR /usr/src/app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/hypercorn /usr/local/bin/hypercorn

RUN apt update \
    && apt install -y libpq5 libxml2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

WORKDIR /usr/src/app
CMD ["hypercorn", "-b", "unix:/var/tmp/hypercorn.sock", "-w","4", "dora_person.main:app","--reload"]
