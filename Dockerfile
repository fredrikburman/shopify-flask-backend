FROM node:latest AS build
ARG API_URL_FOR_SHOPIFY
ENV API_URL_FOR_SHOPIFY=${API_URL_FOR_SHOPIFY}

FROM python:3.9.0-slim-buster AS production
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt --no-cache-dir
COPY . .
COPY --from=build /app/plugin_shopify/templates/*.html plugin_shopify/templates/static/
COPY --from=build /app/plugin_shopify/templates/static/ plugin_shopify/templates/static/
ENV PORT 5000

COPY ./docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]
