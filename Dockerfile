FROM python:3.14-slim AS build
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mkdocs.yml ./
COPY docs ./docs
RUN mkdocs build --strict

FROM nginx:alpine
COPY --from=build /app/site /usr/share/nginx/html
EXPOSE 80
