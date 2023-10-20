all: delete build minishow create

start: build minishow create

build: 
	docker build -t custom-services/gateway-aggregator .

miniload:
	minikube image load docker.io/custom-services/gateway-aggregator

minishow:
	docker image list | grep gateway-aggregator
	minikube image list --format=table | grep gateway-aggregator

refresh: delete create

create:
	kubectl create -f ./service.yaml

delete:
	kubectl delete -f ./service.yaml

reeval:
	eval $(minikube docker-env)
