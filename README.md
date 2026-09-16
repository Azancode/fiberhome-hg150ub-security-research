# fiberhome-hg150ub-security-research
Security research and vulnerability analysis of the FiberHome HG150-Ub VDSL2 modem/router in an isolated lab environment.

## Overview

This repository documents my security research into a FiberHome HG150-Ub VDSL2 modem/router.

The research began with web-interface reconnaissance and authentication/session analysis and progressed to controlled testing of the router's wireless configuration functionality.

The longer-term goal of this project is to understand the device's web application, configuration handling, firmware, and underlying software through reverse engineering.

> **Important:** All testing described in this repository was performed against a device owned/controlled for laboratory research and on an isolated local network.

---

## Device Information

| Property | Value |
|---|---|
| Device | FiberHome HG150-Ub |
| Firmware | HG150-Ub_V3.0 |
| Hardware | HG150-Ub_R3A |
| Board ID | 963381REF1 |
| Web Server | micro_httpd |
| Management IP | 192.168.10.1 |
| Test Environment | Isolated laboratory network |

---

## Research Phases

### Phase 1 — Web Interface Reconnaissance

- Identified exposed TCP services.
- Enumerated the router's HTTP/HTTPS attack surface.
- Examined the web interface and JavaScript.
- Analyzed the login mechanism.
- Mapped configuration-related endpoints.

### Phase 2 — Authentication & Session Analysis

- Examined `login.html` and the login request construction.
- Investigated unauthenticated access to configuration pages.
- Analyzed session-key generation and validation behavior.
- Compared fresh and stale session keys.
- Investigated the relationship between client-side JavaScript and server-side validation.

### Phase 3 — Wireless Configuration Testing

The wireless configuration interface was analyzed to understand how configuration changes are submitted.

The web application constructs requests to:


/wlcfg.wl


The request contains wireless configuration parameters, a checksum value, and a dynamically generated session key.

A controlled test demonstrated that a freshly obtained session key could be used with the correctly calculated request checksum to modify the router's wireless SSID.

The test SSID used during research was:


HACKED-BY-AZAN1


The changed configuration was subsequently verified through the router's wireless configuration page.

### Phase 4 — Firmware Reverse Engineering

**Status: Planned**

Future research will focus on analysis of the firmware and underlying software.

Planned areas include:

* Firmware format identification
* Filesystem extraction
* CGI binary analysis
* Authentication/session implementation
* Configuration handlers
* Startup scripts
* Privileged processes
* Local privilege boundaries
* Potential privilege-escalation paths

No conclusions about firmware-level vulnerabilities will be made until they are experimentally verified.

---

## Key Findings So Far

### Wireless Configuration Exposure

An unauthenticated request to the wireless configuration page was observed to return configuration-related content that would normally be associated with the protected management interface.

The response also contained a dynamically generated session key.

### Session-Key Enforcement

Requests using previously obtained/stale session keys were rejected with:


Invalid Session Key, please try again


This demonstrated that the state-changing wireless configuration endpoint performs server-side session-key validation.

### Controlled Wireless Configuration Modification

A fresh session key obtained from the unauthenticated configuration-page response was accepted by the wireless configuration endpoint when combined with the correctly calculated checksum.

The router's SSID was successfully changed during the controlled laboratory test.

The modification was subsequently verified through the router's configuration interface.

---

## Methodology

The research follows a controlled and reproducible workflow:

1. Reconnaissance
2. Endpoint enumeration
3. Source-code/JavaScript analysis
4. Request reconstruction
5. Session analysis
6. Controlled exploitation
7. Independent verification
8. Evidence collection
9. Firmware analysis

Where possible, findings are supported by HTTP responses, screenshots, request/response captures, hashes, and reproducible test steps.

---

## Evidence

Evidence will be organized separately from the main research notes.


evidence/
├── screenshots/
├── http/
└── nmap/


Sensitive information such as passwords, authentication tokens, cookies, private keys, serial numbers, and configuration backups will not be published.

---

## Future Work

The next major stage of this project is firmware reverse engineering.

The objective is to move from web-interface analysis toward understanding how the router implements:


Web Interface
      ↓
CGI / Backend
      ↓
Configuration Handling
      ↓
System Services
      ↓
Underlying Linux Environment


The firmware analysis will be performed on copies of the original firmware while preserving the original evidence.

---

## Disclaimer

This repository is intended for educational security research and authorized laboratory testing.

The techniques and observations documented here should only be applied to devices and systems for which the researcher has explicit authorization.

---

## Researcher

**Azan**

Security Research / Cybersecurity




