#!/bin/bash

echo "Testing LLM Stack Step 2 endpoints..." 
echo "====================================="

# Test Paperless endpoint
echo "Testing Paperless endpoint (port 8321)..."
if curl -s -f "http://localhost:8321/" > /dev/null; then
    echo "✓ Paperless is accessible at http://localhost:8321"
else
    echo "✗ Paperless is not accessible at http://localhost:8321"
fi

# Test PhotoPrism endpoint
echo "Testing PhotoPrism endpoint (port 2342)..."
if curl -s -f "http://localhost:2342/" > /dev/null; then
    echo "✓ PhotoPrism is accessible at http://localhost:2342"
else
    echo "✗ PhotoPrism is not accessible at http://localhost:2342"
fi

# Test Vision endpoint
echo "Testing Vision endpoint (port 2343)..."
if curl -s "http://localhost:2343/" > /dev/null; then
    echo "✓ Vision service is accessible at http://localhost:2343"
else
    echo "✗ Vision service is not accessible at http://localhost:2343"
fi

echo ""
echo "Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(paperless|photoprism|vision)"

echo ""
echo "Step 2 endpoint testing complete!"
