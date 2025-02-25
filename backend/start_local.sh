#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting development environment...${NC}"


echo -e "${BLUE}Building SAM application...${NC}"
sam build


cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    # Kill background processes
    if [ ! -z "$API_PID" ]; then
        echo "Stopping SAM API..."
        kill $API_PID 2>/dev/null
    fi
    

    echo "Stopping Docker containers for Swagger..."
    SWAGGER_CONTAINER=$(docker ps --filter "ancestor=swaggerapi/swagger-ui" -q)
    if [ ! -z "$SWAGGER_CONTAINER" ]; then
        docker stop $SWAGGER_CONTAINER >/dev/null
    fi
    
    echo -e "${GREEN}All services stopped. Goodbye!${NC}"
    exit 0
}


trap cleanup SIGINT


echo -e "${BLUE}Starting SAM local API on port 3001...${NC}"
sam local start-api --warm-containers EAGER --port 3001 --parameter-overrides "Environment=dev" 2>&1 >/dev/null &
API_PID=$!


sleep 2


if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}SAM API starting (PID: $API_PID)${NC}"
else
    echo -e "${YELLOW}Warning: SAM API process exited unexpectedly.${NC}"
fi


echo -e "${BLUE}Starting Swagger UI on port 80...${NC}"
docker run -d -p 80:8080 \
    -e SWAGGER_JSON=/swagger.yaml \
    -e OAUTH2_REDIRECT_URL=http://localhost/oauth2-redirect.html \
    -e OAUTH_APP_NAME="Student Advisor API" \
    -e SWAGGER_HOST_URL=http://localhost \
    -e OAUTH_CLIENT_ID=29sfsu3nvhqfsjjnimcgh9ejab \
    -v $(pwd)/swagger.yaml:/swagger.yaml \
    swaggerapi/swagger-ui > /dev/null
SWAGGER_CONTAINER=$(docker ps --filter "ancestor=swaggerapi/swagger-ui" -q)


sleep 2


if [ ! -z "$SWAGGER_CONTAINER" ]; then
    echo -e "${GREEN}Swagger UI starting (container ID: $SWAGGER_CONTAINER)${NC}"
else
    echo -e "${YELLOW}Warning: Swagger UI container failed to start.${NC}"
fi

echo -e "${GREEN}Development environment is up and running!${NC}"
echo -e "${BLUE}SAM API:${NC} http://localhost:3001"
echo -e "${BLUE}Swagger UI:${NC} http://localhost"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

echo -e "\n${BLUE}Showing SAM API logs:${NC}"
echo -e "${YELLOW}=====================================================${NC}"


while ps -p $API_PID > /dev/null; do
    sleep 1
done


echo -e "${YELLOW}SAM API process has stopped.${NC}"

cleanup