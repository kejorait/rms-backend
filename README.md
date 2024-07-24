# rms-kejora
 
# Backend Deployment Guide

## Local Testing

```
python -m venv venv
```

Windows

  

  

  

- CMD

  

  

```venv\scripts\activate.bat```

  

  

- Powershell

  

  

```venv\scripts\activate.ps1```

  

  

  

Linux

  

  

  

```
source venv/bin/activate
```

then

  

  

```
pip install -r ./requirements.txt

python ./app.py
```

This guide provides step-by-step instructions for deploying the backend service, including database setup, Docker container management, and environment configuration.

## Database Deployment

First, deploy the PostgreSQL database using Docker:

```
docker run --name kejora-db -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres:alpine3.20
```

## Nginx Setup
Sites example
```
map "$http_origin" $cors {
  default '';
  "~^http?://localhost(:[0-9]+)?$" "$http_origin";
  "~^https?://([a-zA-Z0-9-]+[.])*kejora.my.id(:[0-9]+)?$" "$http_origin";
  "http://127.0.0.1:5500" "$http_origin";
}

server {
    listen 3001 ssl;
    server_name api.kejora.my.id;
    
    ssl_certificate /etc/nginx/ssl/*.kejora.my.id_kejora.my.id_2048/fullchain.cer;
    ssl_certificate_key /etc/nginx/ssl/*.kejora.my.id_kejora.my.id_2048/private.key;
    
    location / {
        if ($cors != "") {
            add_header 'Access-Control-Allow-Origin' "$cors" always; # <-- Variable $cors
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
        }
        # Check if it's a preflight request and "cache" it for 20 days
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' "$cors" always; # <-- Variable $cors
            return 204;
        }
        
        proxy_pass http://172.17.0.4:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }   
}

```
Next, set up the Nginx server with Docker:
```
docker run -dit \
  --name=nginx-ui \
  --restart=always \
  -e TZ=Asia/Taipei \
  -v /mnt/user/appdata/nginx:/etc/nginx \
  -v /mnt/user/appdata/nginx-ui:/etc/nginx-ui \
  -v /var/www:/var/www \
  -p 80:80 -p 3001:3001 -p 8888:8888 \
  uozi/nginx-ui:latest
```
## Building the Backend
Build the backend Docker image:

```
docker build -f .\Dockerfile -t mliem/rms-backend .
docker push mliem/rms-backend
docker system prune -a -f
```
Deploying the Backend
Deploy the backend service:
```
docker rm -f rms-backend
docker system prune -a -f
docker pull mliem/rms-backend
docker run -d --name rms-backend \
  -e SECRET_KEY="topsecretkey" \
  -e PG_USER="postgres" \
  -e PG_PWD="mysecretpassword" \
  -e PG_PORT="5432" \
  -e PG_DB="rms-kejora" \
  -e PG_HOST="172.17.0.2" \
  -e HOST="https://mliem.kejora.my.id:3001/api/v1" \
  -e ENV="DEV" \
  -e MENU_PATH="menu" \
  -e USER_PATH="user" \
  -e CATEGORY_PATH="category" \
  -e UPLOADS_PATH="uploads" \
  -v /root/rms-backend/uploads:/app/uploads \
  mliem/rms-backend
```

## Environment Variables Example
Create a .env file with the following content:
```
SECRET_KEY="topsecretkey"
PG_USER="postgres"
PG_PWD="mysecretpassword"
PG_PORT="5432"
PG_DB="rms-kejora"
PG_HOST="mliem.kejora.my.id"
HOST="https://mliem.kejora.my.id:5000"
ENV="DEV"
MENU_PATH="uploads/menu"
USER_PATH="uploads/user"
CATEGORY_PATH="uploads/category"
```