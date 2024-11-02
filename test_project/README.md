# Test Project

This project demonstrates the use of a custom Netmiko CLI test.

## Setup

To run this test, a Linux container must be active and configured to expose SSH on port 2222.

The GitHub Action workflow initiates the container with the following configuration:

```yaml
    services:
      box01:
        image: ghcr.io/network-unit-testing-system/nuts-testclient:latest
        ports:
          - 2222:22
```

