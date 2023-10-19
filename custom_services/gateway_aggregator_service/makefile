all: delete build miniload minishow create

build: 
	docker build . -t custom-services/gateway-aggregator

miniload: 
	minikube image load custom-services/gateway-aggregator

minishow:
	minikube image ls | grep gateway-aggregator

refresh: delete create

create:
	kubectl create -f ./service.yaml

delete:
	kubectl delete -f ./service.yaml

