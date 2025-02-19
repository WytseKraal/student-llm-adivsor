def lambda_handler(event, context):
    token = event.get("headers", {}).get("x-custom-auth")
    expected_token = "TEST_AUTH_KEY" 

    if token == expected_token:
        return generate_policy("user", "Allow", event["methodArn"])
    else:
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
