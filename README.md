# mcp-pihole

MCP server for Pi-hole v6. Manage blocklists, DNS blocking, domain allow/deny lists, and query diagnostics through the Model Context Protocol.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Pi-hole v6+ with the REST API enabled

## Setup

```bash
uv sync
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PIHOLE_URL` | Yes | Base URL of your Pi-hole instance (e.g., `http://192.168.0.160:8080`) |
| `PIHOLE_PASSWORD` | No | Web interface password. Omit or leave empty for passwordless instances. |

### Claude Code

```bash
claude mcp add pihole \
  -e PIHOLE_URL=http://192.168.0.160:8080 \
  -e PIHOLE_PASSWORD=yourpassword \
  -- uvx mcp-pihole
```

Or add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "pihole": {
      "command": "uvx",
      "args": ["mcp-pihole"],
      "env": {
        "PIHOLE_URL": "http://192.168.0.160:8080",
        "PIHOLE_PASSWORD": "yourpassword"
      }
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "pihole": {
      "command": "uvx",
      "args": ["mcp-pihole"],
      "env": {
        "PIHOLE_URL": "http://192.168.0.160:8080",
        "PIHOLE_PASSWORD": "yourpassword"
      }
    }
  }
}
```

## Tools

### Diagnostics

| Tool | Description |
|------|-------------|
| `get_status` | Pi-hole status summary (queries, blocked count, blocking state) |
| `get_top_domains` | Top queried or blocked domains |
| `get_top_clients` | Top DNS clients by query count |
| `get_queries` | Recent DNS query log with cursor-based pagination |
| `get_version` | Pi-hole FTL version information |

### Blocklist Management

| Tool | Description |
|------|-------------|
| `get_lists` | List all configured blocklists |
| `add_list` | Add a blocklist URL |
| `remove_list` | Remove a blocklist by URL |
| `update_list` | Enable/disable a blocklist or update its comment |
| `update_gravity` | Rebuild gravity database (required after blocklist changes) |

### Domain Management

| Tool | Description |
|------|-------------|
| `get_domains` | List allow/deny domains (exact or regex) |
| `add_domain` | Add a domain to allow or deny list |
| `remove_domain` | Remove a domain from allow or deny list |
| `search_domains` | Check if a domain is blocked and by which list |

### DNS Control and DHCP

| Tool | Description |
|------|-------------|
| `get_blocking_status` | Current DNS blocking status and timer |
| `set_blocking` | Enable/disable blocking, optionally with a timer |
| `get_dhcp_leases` | Current DHCP leases |
| `restart_dns` | Restart the DNS resolver |

## Development

```bash
uv sync
uv run pytest tests/ -x -q
uv run ruff check src/ tests/
uv run pyright src/
```
