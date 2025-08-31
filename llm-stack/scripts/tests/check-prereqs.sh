#!/bin/bash

echo "Checking Docker Desktop, disk space, and ports..." 

# Check Docker version
if command -v docker &> /dev/null; then
    echo "✓ Docker found: $(docker --version)"
else
    echo "✗ Docker not found or not running"
    exit 1
fi

# Check if Docker is running
if docker info &> /dev/null; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running"
    exit 1
fi

# Check disk space (C: drive on Windows)
if command -v df &> /dev/null; then
    # For WSL, check available space
    available_gb=$(df /c 2>/dev/null | awk 'NR==2 {print int($4/1024/1024)}')
    if [ "$available_gb" -ge 50 ]; then
        echo "✓ Sufficient disk space: ${available_gb} GB free"
    else
        echo "✗ Insufficient disk space: ${available_gb} GB free (need 50 GB minimum)"
        exit 1
    fi
else
    echo "⚠ Disk space check skipped (df not available)"
fi

# Check if ports are available
ports=(8321 2342 2343)
for port in "${ports[@]}"; do
    if netstat -an 2>/dev/null | grep ":$port " | grep LISTEN > /dev/null; then
        echo "✗ Port $port is already in use"
        exit 1
    else
        echo "✓ Port $port is available"
    fi
done

echo ""
echo "All prerequisites check passed! ✓"
echo "Ready to proceed with Step 2 setup."
