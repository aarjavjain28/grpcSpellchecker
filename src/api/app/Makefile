.PHONY: compile-proto check-env

export SERVER_PORT=8081


all: python-reqs python-test-reqs setup compile-proto check-env run-tests





python-reqs: requirements.txt
	pip install --upgrade -r requirements2.txt ;  pip install --upgrade -r tests/requirements.txt

python-test-reqs: requirements.txt
	pip install --upgrade -r tests/requirements.txt


setup: python-reqs

compile-proto:

	python -m grpc.tools.protoc \
	--proto_path=./protos \
	--python_out=. \
	--grpc_python_out=. \
	--pyi_out=. \
	./protos/predictor.proto
	echo compile-proto done

check-env:
ifndef SERVER_PORT
	$(error SERVER_PORT is undefined)
endif

run-tests:
	python -m pytest tests/





