# mcp-pihole

MCP server for Pi-hole v6

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pihole": {
      "command": "uvx",
      "args": ["mcp-pihole"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add pihole -- uvx mcp-pihole
```

## Tools

<!-- Add your MCP tools here -->

## Development

```bash
uv sync
uv run pytest tests/ -x -q
uv run ruff check src/ tests/
uv run pyright src/
```
