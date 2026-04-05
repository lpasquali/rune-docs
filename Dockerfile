FROM python:3.14-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mkdocs.yml ./
COPY docs ./docs
RUN mkdocs build --strict

FROM nginx:1.27.4-alpine
COPY --from=build /app/site /usr/share/nginx/html
EXPOSE 80
