# Smart Plugs Management System

Before running the agent, you must start the required backend services:

1. Start the Smart Plug service:
```bash
SmartPlugsManagementSystem/smartplugservice/main.py
```
2. Start the MCP server: 
```bash
SmartPlugsManagementSystem/smartplugsmcp/smartplug_mcp_server.py
```
3. Once both services are running, launch the agent:

Once both services are running, you can launch `main.py` to interact with the agent via a simple cli chat interface.

```bash
SmartPlugsManagementSystem/smartplugagent/main.py
```