# LLM Stack Runbook

Operational procedures and troubleshooting guide for the LLM Stack platform.

## 🚨 Emergency Procedures

### Service Outages
1. **Check Docker status**: `docker ps -a`
2. **Restart services**: `docker compose restart`
3. **Check logs**: `docker compose logs [service-name]`
4. **Full restart**: `docker compose down && docker compose up -d`

### Data Loss Prevention
- Regular backups of `data/` directory
- Export critical documents before major updates
- Monitor disk space usage

## 🔧 Daily Operations

### Health Checks
```powershell
# Check all services
.\scripts\tests\check-prereqs.ps1

# Verify folder structure
.\scripts\tests\check-folders.ps1

# Test service endpoints
.\scripts\smoke\paperless.ps1
.\scripts\smoke\photoprism.ps1
```

### Monitoring
- **Paperless**: http://localhost:8000
- **PhotoPrism**: http://localhost:2342
- **Vision**: http://localhost:2343
- **Disk usage**: Monitor `C:\Ideas\SearchMyFiles\llm-stack\data\`

## 📊 Performance Tuning

### Paperless Optimization
- Adjust `PAPERLESS_CONSUMER_POLLING` in `.env`
- Monitor PostgreSQL performance
- Optimize OCR settings for your use case

### PhotoPrism Optimization
- Adjust `PHOTOPRISM_WORKERS` based on CPU cores
- Monitor Vision service response times
- Optimize thumbnail generation settings

## 🐛 Troubleshooting

### Common Issues

#### Docker Compose Fails
```powershell
# Check Docker Desktop status
# Verify WSL2 backend is enabled
# Restart Docker Desktop if needed
```

#### Port Conflicts
```powershell
# Check what's using the ports
netstat -ano | findstr :8000
netstat -ano | findstr :2342
netstat -ano | findstr :2343
```

#### Permission Issues
```powershell
# Ensure proper folder permissions
# Run PowerShell as Administrator if needed
# Check Docker volume mounts
```

### Log Analysis
```powershell
# Paperless logs
docker compose logs paperless

# PhotoPrism logs  
docker compose logs photoprism

# Database logs
docker compose logs db
```

## 🔄 Maintenance

### Weekly Tasks
- Review disk usage
- Check service logs for errors
- Verify backup integrity
- Update Docker images if needed

### Monthly Tasks
- Full system health check
- Performance review
- Security updates
- Documentation updates

## 📈 Scaling Considerations

### Storage
- Monitor `data/` directory growth
- Plan for additional storage as needed
- Consider archival strategies for old documents/photos

### Performance
- GPU acceleration for RAG operations
- SSD storage for better I/O performance
- Memory allocation for large document collections

## 🔐 Security

### Access Control
- Secure admin passwords
- Regular password rotation
- Network isolation if needed
- API token management

### Data Protection
- Encrypt sensitive documents
- Regular security updates
- Monitor access logs
- Backup encryption

## 📞 Support

### Self-Service
1. Check this runbook
2. Review service logs
3. Test with minimal configuration
4. Check Docker and system resources

### Escalation
- Document the issue and steps taken
- Collect relevant logs and error messages
- Note system state and recent changes
- Prepare reproduction steps
