
import logging
import json

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    token = event.get("headers", {}).get("x-custom-auth")
    expected_token = "TEST_AUTH_KEY" 

    if token == expected_token:
        logger.info("Token matched, allow")
        return generate_policy("user", "Allow", event["methodArn"])
    else:
        logger.info(f"Token denied: {token}")
        return generate_policy("user", "Deny", event["methodArn"])


def generate_policy(principal_id, effect, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }
    }
