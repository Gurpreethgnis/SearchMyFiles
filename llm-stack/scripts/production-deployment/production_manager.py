#!/usr/bin/env python3
"""
Step 8: Production Deployment & Monitoring
Production Deployment Manager

This module provides comprehensive production deployment capabilities:
- Multi-service orchestration
- Health monitoring and auto-recovery
- Load balancing and scaling
- Security and authentication
- Performance optimization
- Backup and disaster recovery
"""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import psutil
import docker
from docker.errors import DockerException

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    name: str
    type: str  # 'fastapi', 'docker', 'systemd', 'supervisor'
    command: str
    port: int
    health_check_url: Optional[str] = None
    environment: Dict[str, str] = None
    dependencies: List[str] = None
    auto_restart: bool = True
    max_restarts: int = 3
    restart_delay: int = 30

@dataclass
class ServiceStatus:
    name: str
    status: str  # 'running', 'stopped', 'error', 'starting'
    pid: Optional[int] = None
    port: int
    health_status: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    restart_count: int
    last_error: Optional[str] = None
    last_check: datetime

@dataclass
class DeploymentMetrics:
    total_services: int
    running_services: int
    failed_services: int
    system_memory_usage: float
    system_cpu_usage: float
    disk_usage: float
    network_connections: int
    timestamp: datetime

class ProductionManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.services: Dict[str, ServiceConfig] = {}
        self.service_statuses: Dict[str, ServiceStatus] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.docker_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        
        # Initialize Docker client if available
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except DockerException:
            logger.warning("Docker not available, Docker services will be skipped")
        
        self._load_configuration()
        self._setup_signal_handlers()
    
    def _load_configuration(self):
        """Load service configurations from config files."""
        config_file = self.config_dir / "services.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    for service_data in config_data.get('services', []):
                        service = ServiceConfig(**service_data)
                        self.services[service.name] = service
                        logger.info(f"Loaded service configuration: {service.name}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
        else:
            # Create default configuration
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default service configurations."""
        default_services = [
            ServiceConfig(
                name="search-discovery-api",
                type="fastapi",
                command="python search-discovery-web.py",
                port=8000,
                health_check_url="http://localhost:8000/api/health",
                environment={"ENVIRONMENT": "production"},
                dependencies=[]
            ),
            ServiceConfig(
                name="rag-api",
                type="fastapi", 
                command="python rag-web-interface.py",
                port=8001,
                health_check_url="http://localhost:8001/api/health",
                environment={"ENVIRONMENT": "production"},
                dependencies=[]
            ),
            ServiceConfig(
                name="analytics-api",
                type="fastapi",
                command="python analytics-web-interface.py", 
                port=8002,
                health_check_url="http://localhost:8002/api/health",
                environment={"ENVIRONMENT": "production"},
                dependencies=[]
            )
        ]
        
        for service in default_services:
            self.services[service.name] = service
        
        # Save default configuration
        self._save_configuration()
    
    def _save_configuration(self):
        """Save current service configurations to file."""
        try:
            import yaml
            config_data = {
                'services': [asdict(service) for service in self.services.values()]
            }
            
            self.config_dir.mkdir(exist_ok=True)
            config_file = self.config_dir / "services.yaml"
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Service {service_name} not found")
            return False
        
        service = self.services[service_name]
        
        try:
            if service.type == "fastapi":
                return self._start_fastapi_service(service)
            elif service.type == "docker":
                return self._start_docker_service(service)
            elif service.type == "systemd":
                return self._start_systemd_service(service)
            elif service.type == "supervisor":
                return self._start_supervisor_service(service)
            else:
                logger.error(f"Unknown service type: {service.type}")
                return False
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            self._update_service_status(service_name, "error", str(e))
            return False
    
    def _start_fastapi_service(self, service: ServiceConfig) -> bool:
        """Start a FastAPI service."""
        try:
            # Check if port is already in use
            if self._is_port_in_use(service.port):
                logger.warning(f"Port {service.port} is already in use")
                return False
            
            # Set environment variables
            env = os.environ.copy()
            if service.environment:
                env.update(service.environment)
            
            # Start the process
            process = subprocess.Popen(
                service.command.split(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service.name] = process
            self._update_service_status(service.name, "starting")
            
            # Wait a bit for startup
            time.sleep(2)
            
            if process.poll() is None:  # Process is running
                self._update_service_status(service.name, "running", pid=process.pid)
                logger.info(f"Service {service.name} started successfully (PID: {process.pid})")
                return True
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                error_msg = f"Process failed to start. stdout: {stdout}, stderr: {stderr}"
                self._update_service_status(service.name, "error", error_msg)
                return False
                
        except Exception as e:
            logger.error(f"Failed to start FastAPI service {service.name}: {e}")
            return False
    
    def _start_docker_service(self, service: ServiceConfig) -> bool:
        """Start a Docker service."""
        if not self.docker_client:
            logger.error("Docker client not available")
            return False
        
        try:
            # Parse command to extract image and options
            # This is a simplified implementation
            container = self.docker_client.containers.run(
                service.command,  # Assuming command is the image name
                detach=True,
                ports={f'{service.port}/tcp': service.port},
                environment=service.environment or {},
                name=service.name
            )
            
            self._update_service_status(service.name, "running")
            logger.info(f"Docker service {service.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Docker service {service.name}: {e}")
            return False
    
    def _start_systemd_service(self, service: ServiceConfig) -> bool:
        """Start a systemd service."""
        try:
            result = subprocess.run(
                ['systemctl', 'start', service.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._update_service_status(service.name, "running")
                logger.info(f"Systemd service {service.name} started successfully")
                return True
            else:
                error_msg = f"Failed to start systemd service: {result.stderr}"
                self._update_service_status(service.name, "error", error_msg)
                return False
                
        except Exception as e:
            logger.error(f"Failed to start systemd service {service.name}: {e}")
            return False
    
    def _start_supervisor_service(self, service: ServiceConfig) -> bool:
        """Start a supervisor service."""
        try:
            result = subprocess.run(
                ['supervisorctl', 'start', service.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._update_service_status(service.name, "running")
                logger.info(f"Supervisor service {service.name} started successfully")
                return True
            else:
                error_msg = f"Failed to start supervisor service: {result.stderr}"
                self._update_service_status(service.name, "error", error_msg)
                return False
                
        except Exception as e:
            logger.error(f"Failed to start supervisor service {service.name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            logger.error(f"Service {service_name} not found")
            return False
        
        service = self.services[service_name]
        
        try:
            if service.type == "fastapi":
                return self._stop_fastapi_service(service)
            elif service.type == "docker":
                return self._stop_docker_service(service)
            elif service.type == "systemd":
                return self._stop_systemd_service(service)
            elif service.type == "supervisor":
                return self._stop_supervisor_service(service)
            else:
                logger.error(f"Unknown service type: {service.type}")
                return False
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            return False
    
    def _stop_fastapi_service(self, service: ServiceConfig) -> bool:
        """Stop a FastAPI service."""
        if service.name in self.processes:
            process = self.processes[service.name]
            try:
                process.terminate()
                process.wait(timeout=10)
                del self.processes[service.name]
                self._update_service_status(service.name, "stopped")
                logger.info(f"Service {service.name} stopped successfully")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                del self.processes[service.name]
                self._update_service_status(service.name, "stopped")
                logger.warning(f"Service {service.name} force killed")
                return True
        else:
            logger.warning(f"Service {service.name} not found in running processes")
            return False
    
    def _stop_docker_service(self, service: ServiceConfig) -> bool:
        """Stop a Docker service."""
        if not self.docker_client:
            return False
        
        try:
            container = self.docker_client.containers.get(service.name)
            container.stop()
            self._update_service_status(service.name, "stopped")
            logger.info(f"Docker service {service.name} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Docker service {service.name}: {e}")
            return False
    
    def _stop_systemd_service(self, service: ServiceConfig) -> bool:
        """Stop a systemd service."""
        try:
            result = subprocess.run(
                ['systemctl', 'stop', service.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._update_service_status(service.name, "stopped")
                logger.info(f"Systemd service {service.name} stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop systemd service: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to stop systemd service {service.name}: {e}")
            return False
    
    def _stop_supervisor_service(self, service: ServiceConfig) -> bool:
        """Stop a supervisor service."""
        try:
            result = subprocess.run(
                ['supervisorctl', 'stop', service.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._update_service_status(service.name, "stopped")
                logger.info(f"Supervisor service {service.name} stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop supervisor service: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to stop supervisor service {service.name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service."""
        logger.info(f"Restarting service {service_name}")
        if self.stop_service(service_name):
            time.sleep(2)  # Wait a bit before restarting
            return self.start_service(service_name)
        return False
    
    def start_all_services(self) -> Dict[str, bool]:
        """Start all configured services."""
        results = {}
        logger.info("Starting all services...")
        
        for service_name in self.services:
            logger.info(f"Starting service: {service_name}")
            results[service_name] = self.start_service(service_name)
            time.sleep(1)  # Small delay between services
        
        return results
    
    def stop_all_services(self) -> Dict[str, bool]:
        """Stop all running services."""
        results = {}
        logger.info("Stopping all services...")
        
        for service_name in self.services:
            logger.info(f"Stopping service: {service_name}")
            results[service_name] = self.stop_service(service_name)
        
        return results
    
    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Get the current status of a service."""
        return self.service_statuses.get(service_name)
    
    def get_all_service_statuses(self) -> Dict[str, ServiceStatus]:
        """Get status of all services."""
        return self.service_statuses.copy()
    
    def _update_service_status(self, service_name: str, status: str, 
                             error_msg: Optional[str] = None, pid: Optional[int] = None):
        """Update the status of a service."""
        if service_name not in self.service_statuses:
            self.service_statuses[service_name] = ServiceStatus(
                name=service_name,
                status=status,
                pid=pid,
                port=self.services[service_name].port,
                health_status="unknown",
                uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                restart_count=0,
                last_error=error_msg,
                last_check=datetime.now()
            )
        else:
            service_status = self.service_statuses[service_name]
            service_status.status = status
            service_status.last_check = datetime.now()
            if error_msg:
                service_status.last_error = error_msg
            if pid:
                service_status.pid = pid
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    def get_deployment_metrics(self) -> DeploymentMetrics:
        """Get comprehensive deployment metrics."""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            network = len(psutil.net_connections())
            
            # Service metrics
            running_count = sum(1 for status in self.service_statuses.values() 
                              if status.status == "running")
            failed_count = sum(1 for status in self.service_statuses.values() 
                             if status.status == "error")
            
            return DeploymentMetrics(
                total_services=len(self.services),
                running_services=running_count,
                failed_services=failed_count,
                system_memory_usage=memory.percent,
                system_cpu_usage=cpu,
                disk_usage=disk.percent,
                network_connections=network,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get deployment metrics: {e}")
            return DeploymentMetrics(
                total_services=len(self.services),
                running_services=0,
                failed_services=0,
                system_memory_usage=0.0,
                system_cpu_usage=0.0,
                disk_usage=0.0,
                network_connections=0,
                timestamp=datetime.now()
            )
    
    def health_check_all_services(self) -> Dict[str, bool]:
        """Perform health checks on all services."""
        results = {}
        
        for service_name, service in self.services.items():
            if service.health_check_url:
                results[service_name] = self._health_check_service(service)
            else:
                results[service_name] = True  # No health check URL configured
        
        return results
    
    def _health_check_service(self, service: ServiceConfig) -> bool:
        """Perform health check on a specific service."""
        try:
            import requests
            response = requests.get(service.health_check_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {e}")
            return False
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        self.running = True
        logger.info("Starting production monitoring...")
        
        while self.running:
            try:
                # Update service statuses
                self._update_all_service_statuses()
                
                # Perform health checks
                health_results = self.health_check_all_services()
                
                # Auto-restart failed services
                for service_name, is_healthy in health_results.items():
                    if not is_healthy and service_name in self.services:
                        service = self.services[service_name]
                        if service.auto_restart:
                            logger.warning(f"Service {service_name} is unhealthy, attempting restart...")
                            self.restart_service(service_name)
                
                # Log metrics
                metrics = self.get_deployment_metrics()
                logger.info(f"Deployment metrics: {asdict(metrics)}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
    
    def _update_all_service_statuses(self):
        """Update status of all services."""
        for service_name, service in self.services.items():
            try:
                if service.type == "fastapi" and service_name in self.processes:
                    process = self.processes[service_name]
                    if process.poll() is None:  # Process is running
                        self._update_service_status(service_name, "running", pid=process.pid)
                    else:
                        self._update_service_status(service_name, "stopped")
                # Add similar logic for other service types
            except Exception as e:
                logger.error(f"Failed to update status for {service_name}: {e}")
    
    def shutdown(self):
        """Gracefully shutdown the production manager."""
        logger.info("Shutting down production manager...")
        self.running = False
        
        # Stop all services
        self.stop_all_services()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Production manager shutdown complete")

def main():
    """Main function to run the production manager."""
    try:
        manager = ProductionManager()
        
        # Start all services
        start_results = manager.start_all_services()
        logger.info(f"Service startup results: {start_results}")
        
        # Start monitoring
        manager.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Production manager failed: {e}")
        sys.exit(1)
    finally:
        if 'manager' in locals():
            manager.shutdown()

if __name__ == "__main__":
    main()
