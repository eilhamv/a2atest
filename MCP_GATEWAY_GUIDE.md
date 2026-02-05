# MCP ContextForge Gateway - Quick Start Guide

## Starting the Server

### Method 1: Using the command line
```bash
# Activate the conda environment
conda activate mcpdemo

# Start the server
mcpgateway mcpgateway.main:app
```

The server will start on **http://localhost:4444**

### Method 2: Start with custom port
```bash
conda activate mcpdemo
mcpgateway mcpgateway.main:app --port 8080
```

### Method 3: Start in background (production)
```bash
conda activate mcpdemo
nohup mcpgateway mcpgateway.main:app > mcpgateway.log 2>&1 &
```

## Checking if Server is Running

### Method 1: Check the process
```bash
ps aux | grep mcpgateway | grep -v grep
```
If running, you'll see output like:
```
harishankar  93298  0.0  0.3 ... /path/to/python ... mcpgateway mcpgateway.main:app
```

### Method 2: Check the port
```bash
lsof -i :4444
```
If running, you'll see the process using port 4444.

### Method 3: Test with curl
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:4444/
```
If running, you'll get a response code (like `303` or `200`).

### Method 4: Open in browser
Simply visit: **http://localhost:4444/admin/login**

If the login page loads, the server is running.

## Stopping the Server

### If running in terminal (foreground):
Press `Ctrl+C` in the terminal where the server is running.

### If running in background:
```bash
# Find the process ID
ps aux | grep mcpgateway | grep -v grep

# Kill the process (replace PID with actual process ID)
kill <PID>

# Or force kill if needed
kill -9 <PID>
```

### Quick stop command:
```bash
pkill -f mcpgateway
```

## Admin Access

- **URL**: http://localhost:4444/admin/login
- **Email**: admin@example.com
- **Password**: changeme (change on first login)

## Server Logs

Logs are written to:
- Console output (if running in foreground)
- `logs/mcpgateway.log` (configured in .env)
- `mcpgateway.log` (if using nohup)

View logs in real-time:
```bash
tail -f logs/mcpgateway.log
```

## Troubleshooting

### Port already in use
If port 4444 is already in use, either:
1. Stop the existing process: `lsof -ti:4444 | xargs kill`
2. Use a different port: `mcpgateway mcpgateway.main:app --port 8080`

### Database issues
The database file is `mcp.db` in your working directory. If you need to reset:
```bash
rm mcp.db
# Then restart the server - it will recreate the database
```

### Environment not activated
Always activate the conda environment first:
```bash
conda activate mcpdemo
```

## Quick Reference Commands

```bash
# Start server
conda activate mcpdemo && mcpgateway mcpgateway.main:app

# Check if running
curl -s http://localhost:4444/ -I | head -1

# View logs
tail -f logs/mcpgateway.log

# Stop server
pkill -f mcpgateway
```

## Configuration

Server configuration is in the `.env` file in your working directory.
Key settings:
- `HOST=0.0.0.0` - Bind to all interfaces
- `PORT=4444` - Server port (set via command line)
- `PLATFORM_ADMIN_EMAIL` - Admin email
- `JWT_SECRET_KEY` - JWT signing key (change for production!)
- `AUTH_ENCRYPTION_SECRET` - Auth encryption key (change for production!)

## Production Deployment

For production use:
1. Change all default passwords and secrets in `.env`
2. Use a proper database (PostgreSQL/MySQL instead of SQLite)
3. Use a process manager like systemd or supervisor
4. Set up proper logging and monitoring
5. Use HTTPS with proper SSL certificates

## Support

- Documentation: https://ibm.github.io/mcp-context-forge/
- PyPI: https://pypi.org/project/mcp-contextforge-gateway/