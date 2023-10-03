ARG ARCH=
ARG PY_VERSION=3.9.16-slim
ARG BASE_IMAGE=public.ecr.aws/docker/library/python:$PY_VERSION
ARG LAMBDA_IMAGE=public.ecr.aws/lambda/python:latest
FROM $BASE_IMAGE as builder

WORKDIR /opt
RUN python -m pip install pip -U
RUN pip install poetry
COPY cdk_gw_tools /opt/cdk_gw_tools
COPY pyproject.toml poetry.lock README.md LICENSE /opt/
RUN poetry build

FROM $BASE_IMAGE as from-build
COPY --from=builder /opt/dist/cdk_gw_tools-*.whl /opt/
WORKDIR /opt
RUN pip install pip -U --no-cache-dir && pip install wheel --no-cache-dir && pip install *.whl --no-cache-dir
WORKDIR /tmp
ENV AWS_CONFIG_FILE /tmp/.aws/config
ENV AWS_SHARED_CREDENTIALS_FILE /tmp/.aws/credentials
ENTRYPOINT ["cdk-cli"]
