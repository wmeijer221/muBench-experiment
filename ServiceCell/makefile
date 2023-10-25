
bp: build push

build: 
	docker build -t wmeijer221/microservice_v4-screen -f ./Dockerfile-mp.debug .

push:	
	docker push wmeijer221/microservice_v4-screen

better_make: 
	docker build -t wmeijer221/microservice_v4-screen -f ./Dockerfile-mp.debug . --no-cache

bbp: better_make push
