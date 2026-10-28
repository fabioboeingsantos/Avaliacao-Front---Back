FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_URL_DA_API=/api
ENV VITE_URL_DA_API=${VITE_URL_DA_API}
RUN npm run build

FROM caddy:2-alpine

COPY --from=build /app/dist /srv

EXPOSE 80
