docker-compose down
docker container stop $(docker container ls -qa)
docker container rm $(docker container ls -qa)
docker images rm $(docker images ls -q)
