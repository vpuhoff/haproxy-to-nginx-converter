import re

def haproxy_to_nginx(haproxy_config):
    nginx_config = []

    server_directives = []
    upstream_options = []
    ssl_directives = []
    acl_rules = []
    use_backend_rules = []

    # Parse HAProxy config
    for line in haproxy_config.splitlines():
        line = line.strip()

        # Skip comments
        if line.startswith('#') or not line:
            continue

        # Convert global settings
        if line.startswith('global'):
            nginx_config.append('# Global settings (partially converted)')
            continue
        if "log" in line:
            nginx_config.append(f'    # Logging is not directly supported in Nginx: {line}')
            continue
        if "maxconn" in line:
            nginx_config.append(f'    worker_connections {line.split()[1]};')
            continue

        # Convert defaults section
        if line.startswith('defaults'):
            nginx_config.append('# Defaults settings (partially converted)')
            continue
        if "timeout" in line:
            if "connect" in line:
                nginx_config.append(f'    proxy_connect_timeout {line.split()[2].replace("ms", "")}ms;')
            elif "client" in line:
                nginx_config.append(f'    client_body_timeout {line.split()[2].replace("ms", "")}ms;')
            elif "server" in line:
                nginx_config.append(f'    proxy_read_timeout {line.split()[2].replace("ms", "")}ms;')
            continue
        if "option" in line and "httplog" in line:
            nginx_config.append('    access_log /var/log/nginx/access.log;')
            continue

        # Convert frontend
        if line.startswith('frontend'):
            frontend_name = line.split()[1]
            nginx_config.append(f'http {{ # Frontend: {frontend_name}')
            continue

        # Convert backend
        if line.startswith('backend'):
            backend_name = line.split()[1]
            nginx_config.append(f'upstream {backend_name} {{')
            continue

        # Handle SSL certificates
        if line.startswith("bind"):
            bind_params = line.split()[1:]
            for param in bind_params:
                if param.startswith("ssl"):
                    ssl_directives.append("    ssl on;")
                elif param.startswith("crt"):
                    cert_path = param.split("=", 1)[-1]
                    ssl_directives.append(f"    ssl_certificate {cert_path};")
                elif param.startswith("key"):
                    key_path = param.split("=", 1)[-1]
                    ssl_directives.append(f"    ssl_certificate_key {key_path};")
                elif param.startswith("alpn"):
                    alpn_values = param.split("=", 1)[-1]
                    ssl_directives.append(f"    ssl_protocols {alpn_values};")
            continue

        # Convert ACL rules
        acl_match = re.match(r'acl\s+(\S+)\s+(.+)', line)
        if acl_match:
            acl_name = acl_match.group(1)
            acl_condition = acl_match.group(2)
            nginx_condition = acl_condition.replace('hdr', '$http').replace('path_beg', 'starts_with')
            acl_rules.append(f'    set $acl_{acl_name} "{nginx_condition}";')
            continue

        # Convert use_backend rules
        use_backend_match = re.match(r'use_backend\s+(\S+)\s+if\s+(.+)', line)
        if use_backend_match:
            backend_name = use_backend_match.group(1)
            acl_condition = use_backend_match.group(2)
            nginx_condition = acl_condition.replace('hdr', '$http').replace('path_beg', 'starts_with')
            use_backend_rules.append(f'    if ({nginx_condition}) {{')
            use_backend_rules.append(f'        proxy_pass http://{backend_name};')
            use_backend_rules.append(f'    }}')
            continue

        # Convert server definitions
        server_match = re.match(r'server\s+(\S+)\s+(\S+)(.*)', line)
        if server_match:
            server_name = server_match.group(1)
            server_address = server_match.group(2)
            options = server_match.group(3).strip()

            server_line = f'    server {server_address};  # {server_name}'
            if "check" in options:
                server_line = server_line.replace(";", " health_check;")
            server_directives.append(server_line)
            continue

        # Convert balance methods
        if line.startswith("balance"):
            balance_method = line.split()[1]
            if balance_method in ["roundrobin", "leastconn"]:
                upstream_options.append(f'    {balance_method};')
            else:
                upstream_options.append(f'    # Unsupported balance method: {balance_method}')
            continue

        # Add unsupported settings as comments
        nginx_config.append(f'# Unsupported setting: {line}')

    # Close all open blocks
    if upstream_options:
        nginx_config.extend(upstream_options)
    if server_directives:
        nginx_config.extend(server_directives)
    if acl_rules:
        nginx_config.extend(acl_rules)
    if use_backend_rules:
        nginx_config.extend(use_backend_rules)

    nginx_config.append('}')
    return '\n'.join(nginx_config)


# Example usage:
haproxy_example_config = """
global
    log /dev/log local0
    maxconn 4096

defaults
    log     global
    option  httplog
    timeout connect 5000ms
    timeout client 50000ms

frontend http-in
    bind *:80
    acl is_api path_beg /api
    use_backend api_backend if is_api

backend api_backend
    balance roundrobin
    server api1 192.168.1.1:80 check
"""

nginx_config = haproxy_to_nginx(haproxy_example_config)
print(nginx_config)
