## build coomand
docker build --build-arg SERVER_PORT=$(grep SERVER_PORT .env | cut -d '=' -f2) -t ASFES .
