FROM node:18-alpine as base
WORKDIR /app
COPY package*.json ./

FROM base as development
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM base as build
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
