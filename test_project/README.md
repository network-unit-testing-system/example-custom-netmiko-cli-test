# Test Project

This project demonstrates the use of the custom netmiko cli test

## Setup

A Linux container needs to be running and expose SSH over port 2222

The GitHub Action workflow stats the container:

```yaml
    services:
      box01:
        image: ghcr.io/network-unit-testing-system/nuts-testclient:latest
        ports:
          - 2222:22
```

