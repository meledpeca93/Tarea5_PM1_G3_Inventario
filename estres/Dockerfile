FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       stress-ng \
       procps \
       util-linux \
       hostname \
    && rm -rf /var/lib/apt/lists/*

CMD ["stress-ng", "--help"]
