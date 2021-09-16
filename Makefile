name ?= debian-kernel-builder

docker-enter: docker-build
	docker run \
	  -v $(CURDIR):/home/builder/workspace \
	  -it ${name}

docker-build:
	docker build --build-arg uid=$(shell id -u) -t ${name} docker
