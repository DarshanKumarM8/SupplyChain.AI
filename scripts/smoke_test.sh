#!/bin/bash
# To make this script executable, run:
# chmod +x scripts/smoke_test.sh
#
# Usage:
#   ./scripts/smoke_test.sh <DEPLOYMENT_URL>
# Example:
#   ./scripts/smoke_test.sh https://supplychainai-backend.onrender.com

if [ -z "$1" ]; then
    echo "Error: Deployment URL argument missing."
    echo "Usage: $0 <DEPLOYMENT_URL>"
    exit 1
fi

# Remove trailing slash if provided
BASE_URL="${1%/}"
HEALTH_URL="${BASE_URL}/health"

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Pinging ${HEALTH_URL}..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}")

if [ "${HTTP_STATUS}" -eq 200 ]; then
    echo -e "${GREEN}Cloud Deployment Active${NC}"
    exit 0
else
    echo -e "${RED}Error: Health check failed with HTTP status code ${HTTP_STATUS}${NC}"
    exit 1
fi
