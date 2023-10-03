# cdk-gw-tools

CLI & other tools to help automating Conduktor Gateway

### CLI

```bash
cdk-cli -h
usage: CDK Proxy CLI [-h] [--format OUTPUT_FORMAT] [--log-level LOGLEVEL] [--url URL] [--username USERNAME] [--password PASSWORD] [-c CONFIG_FILE] [-p PROFILE_NAME] {vclusters,interceptors,plugins} ...

positional arguments:
  {vclusters,interceptors,plugins}
                        Resources to manage
    vclusters           Manages vClusters
    interceptors        Manage interceptors
    plugins             Manage plugins

options:
  -h, --help            show this help message and exit
  --format OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        output format
  --log-level LOGLEVEL  Set loglevel
  --url URL
  --username USERNAME
  --password PASSWORD
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Path to the profiles files
  -p PROFILE_NAME, --profile-name PROFILE_NAME
                        Name of the profile to use to make API Calls
```

#### Example config file

Config files make it easy to switch between profiles. You can use AWS secrets manager currently to store the credentials
securely and share the config file among teammates.

```yaml
# Conduktor GW CLI Config file
nonprod:
  Url: https://stg.kafka.domain.net:8888
  Username: admin
  Password: somethingsecret

prod:
  Url: https://kafka.prod.domain.net:8888
  AWSSecretsManager:
    SecretId: /conduktor/proxy/prod/apiuser
    ProfileName: aws-prod

```
