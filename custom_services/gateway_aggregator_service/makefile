all: delete start

start: build push create

build: 
	docker build -t wmeijer221/microservice_v4-screen:gateway_aggregator .

push:
	docker push wmeijer221/microservice_v4-screen:gateway_aggregator

refresh: delete create

create:
	kubectl create -f ./service.yaml

delete:
	kubectl delete -f ./service.yaml
