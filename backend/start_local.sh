#!/bin/bash

# Colors for better log visibility
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting development environment...${NC}"

# Build SAM application
echo -e "${BLUE}Building SAM application...${NC}"
sam build

# Function to clean up processes when script is interrupted
cleanup() {
  echo -e "\n${YELLOW}Shutting down services...${NC}"
  
  # Kill background processes
  if [ ! -z "$API_PID" ]; then
    echo "Stopping SAM API..."
    kill $API_PID 2>/dev/null
  fi
  
  if [ ! -z "$SWAGGER_PID" ]; then
    echo "Stopping Swagger UI..."
    kill $SWAGGER_PID 2>/dev/null
  fi
  
  # Find and kill any stray Docker containers related to our services
  echo "Stopping Docker containers..."
  SWAGGER_CONTAINER=$(docker ps --filter "ancestor=swaggerapi/swagger-ui" -q)
  if [ ! -z "$SWAGGER_CONTAINER" ]; then
    docker stop $SWAGGER_CONTAINER >/dev/null
  fi
  
  echo -e "${GREEN}All services stopped. Goodbye!${NC}"
  exit 0
}

# Set trap for SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start SAM local API in background with log file
echo -e "${BLUE}Starting SAM local API on port 3001...${NC}"
sam local start-api --warm-containers EAGER --port 3001 --parameter-overrides "Environment=dev" > sam_api.log 2>&1 &
API_PID=$!

# Wait a moment for API to start initializing
sleep 2

# Check if the process is still running
if ps -p $API_PID > /dev/null; then
  echo -e "${GREEN}SAM API starting (PID: $API_PID)${NC}"
else
  echo -e "${YELLOW}Warning: SAM API process exited unexpectedly. Check sam_api.log for details.${NC}"
fi

# Start Swagger UI in background with log file
echo -e "${BLUE}Starting Swagger UI on port 80...${NC}"
docker run -p 80:8080 \
  -e SWAGGER_JSON=/swagger.yaml \
  -e OAUTH2_REDIRECT_URL=http://localhost/oauth2-redirect.html \
  -e OAUTH_APP_NAME="Student Advisor API" \
  -e SWAGGER_HOST_URL=http://localhost \
  -e OAUTH_CLIENT_ID=29sfsu3nvhqfsjjnimcgh9ejab \
  -v $(pwd)/swagger.yaml:/swagger.yaml \
  swaggerapi/swagger-ui > swagger_ui.log 2>&1 &
SWAGGER_PID=$!

# Wait a moment for Swagger to start
sleep 2

# Check if the process is still running
if ps -p $SWAGGER_PID > /dev/null; then
  echo -e "${GREEN}Swagger UI starting (PID: $SWAGGER_PID)${NC}"
else
  echo -e "${YELLOW}Warning: Swagger UI process exited unexpectedly. Check swagger_ui.log for details.${NC}"
fi

echo -e "${GREEN}Development environment is up and running!${NC}"
echo -e "${BLUE}SAM API:${NC} http://localhost:3001"
echo -e "${BLUE}Swagger UI:${NC} http://localhost"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Display logs in real-time using tail
echo -e "\n${BLUE}Showing combined logs (SAM API and Swagger UI):${NC}"
echo -e "${YELLOW}=====================================================${NC}"

# Use tail to show logs in real-time
tail -f sam_api.log swagger_ui.log

# This line will only execute if tail is interrupted or exits
cleanup