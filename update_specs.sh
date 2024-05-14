#!/usr/bin/env bash

poetry run datamodel-codegen --input cdk_gw_tools/specs/user-mappings.spec.json --input-file-type jsonschema \
    --output cdk_gw_tools/specs/user_mappings.py --output-model-type dataclasses.dataclass \
    --reuse-model --target-python-version 3.10 --disable-timestamp --use-double-quotes \
    --use-field-description --use-schema-description

poetry run datamodel-codegen --input cdk_gw_tools/specs/interceptors-config.spec.json --input-file-type jsonschema \
    --output cdk_gw_tools/specs/interceptors_config.py --output-model-type dataclasses.dataclass \
    --reuse-model --target-python-version 3.10 --disable-timestamp --use-double-quotes \
    --use-field-description --use-schema-description
