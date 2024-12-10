
# HAProxy to Nginx Configuration Converter

This script converts HAProxy configuration files into equivalent Nginx configurations. It handles common directives such as frontend, backend, ACLs, SSL settings, and balancing methods.

---

## Features

- **Global and Defaults Sections**: Partial support for global and default configurations such as `log`, `maxconn`, and timeouts.
- **Frontend to HTTP Block**: Converts HAProxy frontends to Nginx HTTP blocks.
- **Backend to Upstream**: Translates backend servers to upstream blocks in Nginx.
- **SSL Support**: Converts SSL certificates, keys, and ALPN protocols.
- **ACL Rules**: Converts HAProxy ACLs into Nginx `if` conditions or variables.
- **Balancing Methods**: Supports `roundrobin` and `leastconn`.
- **Health Checks**: Translates health check options where applicable.
- **Sticky Sessions**: Converts HAProxy cookie-based sticky sessions into Nginx equivalents.

---

## Requirements

- Python 3.6 or higher.

---

## Installation

1. Clone the repository or download the script:
   ```bash
   git clone <repository_url>
   cd haproxy-to-nginx
   ```

2. Ensure Python is installed:
   ```bash
   python3 --version
   ```

---

## Usage

1. Save your HAProxy configuration in a file, e.g., `haproxy.cfg`.

2. Run the script:
   ```bash
   python3 converter.py
   ```

3. Input your HAProxy configuration when prompted or modify the example configuration inside the script.

4. The converted Nginx configuration will be printed to the console. Redirect it to a file if needed:
   ```bash
   python3 converter.py > nginx.conf
   ```

---

## Example

### Input (HAProxy Configuration)

\`\`\`haproxy
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
\`\`\`

### Output (Nginx Configuration)

\`\`\`nginx
# Global settings (partially converted)
    # Logging is not directly supported in Nginx: log /dev/log local0
    worker_connections 4096;

# Defaults settings (partially converted)
    access_log /var/log/nginx/access.log;
    proxy_connect_timeout 5000ms;
    client_body_timeout 50000ms;

http { # Frontend: http-in
    set $acl_is_api "starts_with /api";

    if ($http_starts_with /api) {
        proxy_pass http://api_backend;
    }

    upstream api_backend {
        roundrobin;
        server 192.168.1.1:80;  # api1
    }
}
\`\`\`

---

## Limitations

- Not all HAProxy directives have direct equivalents in Nginx.
- Logs and monitoring settings are added as comments since they differ significantly.
- Advanced ACLs may require manual adjustments.

---

## Contributing

Contributions are welcome! If you encounter issues or have ideas for enhancements, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

Developed by [Your Name or Team].
