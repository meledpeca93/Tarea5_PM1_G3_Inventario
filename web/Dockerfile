FROM nginx:stable-alpine

LABEL grupo="3"
LABEL componente="Almacenamiento-Web"

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY index.html /usr/share/nginx/html/index.html
COPY app.js /usr/share/nginx/html/app.js
COPY styles.css /usr/share/nginx/html/styles.css

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
