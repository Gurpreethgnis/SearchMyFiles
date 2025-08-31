#!/usr/bin/env python3
"""
Step 8: Production Deployment & Monitoring
Monitoring Dashboard

This module provides a comprehensive monitoring dashboard:
- Real-time service status monitoring
- System resource monitoring
- Performance metrics visualization
- Alert management
- Log aggregation and analysis
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import asyncio
import psutil
import requests
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Production Monitoring Dashboard",
    description="Step 8: Production Deployment & Monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# HTML template for the monitoring dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Production Monitoring Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 {
            margin: 0;
            color: #1e3c72;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            color: #666;
            font-size: 1.1em;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .dashboard-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .dashboard-card h3 {
            margin-top: 0;
            color: #1e3c72;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .status-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border-left: 4px solid #28a745;
        }
        .status-item.error {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        .status-item.warning {
            border-left-color: #ffc107;
            background: #fff3cd;
        }
        .status-item.stopped {
            border-left-color: #6c757d;
            background: #e9ecef;
        }
        .status-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        .status-value {
            font-size: 1.2em;
            font-weight: 500;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .metric-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: 600;
            color: #1e3c72;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            height: 300px;
            margin-top: 20px;
        }
        .log-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 5px;
        }
        .log-entry.info { background: #d1ecf1; }
        .log-entry.warning { background: #fff3cd; }
        .log-entry.error { background: #f8d7da; }
        .refresh-btn {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 20px;
            font-weight: 500;
            z-index: 1000;
        }
        .connected {
            background: #d4edda;
            color: #155724;
        }
        .disconnected {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Production Monitoring Dashboard</h1>
            <p>Step 8: Production Deployment & Monitoring - Real-time System Status</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        
        <div class="connection-status" id="connectionStatus">Connecting...</div>
        
        <div class="dashboard-grid">
            <!-- Service Status -->
            <div class="dashboard-card">
                <h3>🔍 Service Status</h3>
                <div class="status-grid" id="serviceStatus">
                    <div class="status-item">
                        <div class="status-name">Loading...</div>
                        <div class="status-value">Please wait</div>
                    </div>
                </div>
            </div>
            
            <!-- System Resources -->
            <div class="dashboard-card">
                <h3>💻 System Resources</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="cpuUsage">--</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="memoryUsage">--</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="diskUsage">--</div>
                        <div class="metric-label">Disk Usage</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="networkConnections">--</div>
                        <div class="metric-label">Network Connections</div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="dashboard-card">
                <h3>📊 Performance Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="totalServices">--</div>
                        <div class="metric-label">Total Services</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="runningServices">--</div>
                        <div class="metric-label">Running Services</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="failedServices">--</div>
                        <div class="metric-label">Failed Services</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="uptime">--</div>
                        <div class="metric-label">Uptime</div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Logs -->
            <div class="dashboard-card">
                <h3>📝 Recent Logs</h3>
                <div class="log-container" id="recentLogs">
                    <div class="log-entry info">Loading logs...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;
        
        // Initialize WebSocket connection
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                isConnected = true;
                updateConnectionStatus(true);
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                isConnected = false;
                updateConnectionStatus(false);
                console.log('WebSocket disconnected');
                // Reconnect after 5 seconds
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                isConnected = false;
                updateConnectionStatus(false);
            };
        }
        
        function updateConnectionStatus(connected) {
            const statusEl = document.getElementById('connectionStatus');
            if (connected) {
                statusEl.textContent = '🟢 Connected';
                statusEl.className = 'connection-status connected';
            } else {
                statusEl.textContent = '🔴 Disconnected';
                statusEl.className = 'connection-status disconnected';
            }
        }
        
        function updateDashboard(data) {
            // Update service status
            if (data.service_statuses) {
                updateServiceStatus(data.service_statuses);
            }
            
            // Update system metrics
            if (data.system_metrics) {
                updateSystemMetrics(data.system_metrics);
            }
            
            // Update performance metrics
            if (data.performance_metrics) {
                updatePerformanceMetrics(data.performance_metrics);
            }
            
            // Update logs
            if (data.recent_logs) {
                updateLogs(data.recent_logs);
            }
        }
        
        function updateServiceStatus(serviceStatuses) {
            const container = document.getElementById('serviceStatus');
            container.innerHTML = '';
            
            Object.values(serviceStatuses).forEach(status => {
                const statusItem = document.createElement('div');
                statusItem.className = `status-item ${status.status}`;
                
                statusItem.innerHTML = `
                    <div class="status-name">${status.name}</div>
                    <div class="status-value">${status.status.toUpperCase()}</div>
                    <div style="font-size: 0.8em; margin-top: 5px;">
                        Port: ${status.port} | PID: ${status.pid || 'N/A'}
                    </div>
                `;
                
                container.appendChild(statusItem);
            });
        }
        
        function updateSystemMetrics(metrics) {
            document.getElementById('cpuUsage').textContent = `${metrics.cpu_usage.toFixed(1)}%`;
            document.getElementById('memoryUsage').textContent = `${metrics.memory_usage.toFixed(1)}%`;
            document.getElementById('diskUsage').textContent = `${metrics.disk_usage.toFixed(1)}%`;
            document.getElementById('networkConnections').textContent = metrics.network_connections;
        }
        
        function updatePerformanceMetrics(metrics) {
            document.getElementById('totalServices').textContent = metrics.total_services;
            document.getElementById('runningServices').textContent = metrics.running_services;
            document.getElementById('failedServices').textContent = metrics.failed_services;
            document.getElementById('uptime').textContent = formatUptime(metrics.uptime);
        }
        
        function updateLogs(logs) {
            const container = document.getElementById('recentLogs');
            container.innerHTML = '';
            
            logs.slice(-20).forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry ${log.level}`;
                logEntry.textContent = `[${log.timestamp}] ${log.message}`;
                container.appendChild(logEntry);
            });
            
            container.scrollTop = container.scrollHeight;
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
        
        async function refreshData() {
            try {
                const response = await fetch('/api/dashboard-data');
                if (response.ok) {
                    const data = await response.json();
                    updateDashboard(data);
                }
            } catch (error) {
                console.error('Failed to refresh data:', error);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
            refreshData();
            
            // Refresh data every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the monitoring dashboard."""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            data = await get_dashboard_data()
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Get comprehensive dashboard data."""
    try:
        # Get system metrics
        system_metrics = get_system_metrics()
        
        # Get service statuses (mock data for now)
        service_statuses = get_mock_service_statuses()
        
        # Get performance metrics
        performance_metrics = get_performance_metrics(service_statuses)
        
        # Get recent logs
        recent_logs = get_recent_logs()
        
        return {
            "system_metrics": system_metrics,
            "service_statuses": service_statuses,
            "performance_metrics": performance_metrics,
            "recent_logs": recent_logs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_system_metrics():
    """Get current system metrics."""
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        network = len(psutil.net_connections())
        
        return {
            "cpu_usage": cpu,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "network_connections": network
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_connections": 0
        }

def get_mock_service_statuses():
    """Get mock service statuses for demonstration."""
    return {
        "search-discovery-api": {
            "name": "search-discovery-api",
            "status": "running",
            "pid": 12345,
            "port": 8000,
            "health_status": "healthy",
            "uptime": 3600.0,
            "memory_usage": 45.2,
            "cpu_usage": 12.5,
            "restart_count": 0,
            "last_error": None,
            "last_check": datetime.now().isoformat()
        },
        "rag-api": {
            "name": "rag-api",
            "status": "running",
            "pid": 12346,
            "port": 8001,
            "health_status": "healthy",
            "uptime": 3600.0,
            "memory_usage": 38.7,
            "cpu_usage": 8.3,
            "restart_count": 0,
            "last_error": None,
            "last_check": datetime.now().isoformat()
        },
        "analytics-api": {
            "name": "analytics-api",
            "status": "stopped",
            "pid": None,
            "port": 8002,
            "health_status": "unhealthy",
            "uptime": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "restart_count": 2,
            "last_error": "Port 8002 already in use",
            "last_check": datetime.now().isoformat()
        }
    }

def get_performance_metrics(service_statuses):
    """Calculate performance metrics from service statuses."""
    total_services = len(service_statuses)
    running_services = sum(1 for s in service_statuses.values() if s["status"] == "running")
    failed_services = sum(1 for s in service_statuses.values() if s["status"] == "error")
    
    return {
        "total_services": total_services,
        "running_services": running_services,
        "failed_services": failed_services,
        "uptime": 3600.0  # Mock uptime
    }

def get_recent_logs():
    """Get recent log entries."""
    return [
        {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": "info",
            "message": "Production monitoring dashboard started successfully"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=1)).strftime("%H:%M:%S"),
            "level": "info",
            "message": "Service search-discovery-api is running on port 8000"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S"),
            "level": "info",
            "message": "Service rag-api is running on port 8001"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=3)).strftime("%H:%M:%S"),
            "level": "warning",
            "message": "Service analytics-api failed to start: Port 8002 already in use"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=4)).strftime("%H:%M:%S"),
            "level": "info",
            "message": "System resources: CPU 12.5%, Memory 45.2%, Disk 23.1%"
        }
    ]

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "monitoring-dashboard"
    }

def main():
    """Main function to run the monitoring dashboard."""
    try:
        logger.info("Starting Production Monitoring Dashboard...")
        logger.info("Dashboard will be available at: http://localhost:8003")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start monitoring dashboard: {e}")
        raise

if __name__ == "__main__":
    main()
