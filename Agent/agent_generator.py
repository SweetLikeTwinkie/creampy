# agent_generator.py
import json
import os
from jinja2 import Environment, FileSystemLoader

# Set up the Jinja2 environment to load templates from the "templates" folder.
env = Environment(loader=FileSystemLoader('templates'))


def generate_agent(config: dict, mode: str = "file"):
    """
    Generate the agent payload.

    :param config: A dictionary with agent configuration.
    :param mode: "file" for file-based agent, "fileless" for a loader.
    :return: The rendered Python code as a string.
    """
    if mode == "file":
        template = env.get_template('agent_template.py.j2')
        rendered_code = template.render(config_json=json.dumps(config, indent=2))
        output_filename = f"agent_{config.get('agent_id')}.py"
    elif mode == "fileless":
        template = env.get_template('loader_template.py.j2')
        # For fileless agents, assume that the full agent payload is hosted at a URL.
        full_agent_url = config.get("agent_payload_url", "https://example.com/agent_payload.py")
        rendered_code = template.render(agent_code_url=full_agent_url)
        output_filename = f"loader_{config.get('agent_id')}.py"
    else:
        raise ValueError("Invalid mode. Choose 'file' or 'fileless'.")

    # Write the generated code to a file.
    with open(output_filename, "w") as f:
        f.write(rendered_code)

    print(f"Agent generated and saved as {output_filename}")


if __name__ == "__main__":
    # Sample configuration for the agent.
    config = {
        "agent_id": "agent_001",
        "auth_token": "sample_token_123",
        "poll_interval": 10,
        "protocols": {
            "http": {
                "enabled": True,
                "server_url": "http://localhost:8000"
            },
            "dns": {
                "enabled": True,
                "dns_server_ip": "127.0.0.1"
            },
            "icmp": {
                "enabled": False,
                "target_ip": "127.0.0.1"
            },
            "smb": {
                "enabled": True,
                "server_ip": "127.0.0.1"
            }
        },
        # For fileless agents, the full agent payload must be hosted at this URL.
        "agent_payload_url": "https://yourserver.com/agent_payload.py"
    }

    # Operator chooses mode: "file" for file-based agent, "fileless" for in-memory loader.
    mode = input("Enter mode ('file' for file-based agent, 'fileless' for in-memory loader): ").strip()
    generate_agent(config, mode)
