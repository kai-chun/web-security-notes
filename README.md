# web-security-notes
Web Security Learning Notes

## Projects
- SQL Injection → [repo link]

## Skills Demonstrated
- Vulnerability analysis
- Secure coding practices
- Exploit development

## Setup
```
cd {category}/{lab_name}

# Start Python stack (vuln-py on 8001)
docker compose --profile py up

# Start Go stack (vuln-go on 8002)
docker compose --profile go up

# Start both stacks for side-by-side comparison
docker compose --profile py --profile go up

# Run in background
docker compose --profile py up -d
```