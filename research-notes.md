
# Research Notes

Detailed chronological notes from security research performed against a FiberHome HG150-Ub VDSL2 modem/router in an isolated laboratory environment.

---

## 1. Scope and Laboratory Environment

### Target

- Device: FiberHome HG150-Ub
- Firmware: HG150-Ub_V3.0
- Hardware: HG150-Ub_R3A
- Board ID: 963381REF1
- Management IP: `192.168.10.1`

### Test Machine

- Operating System: Kali Linux
- Lab IP: `192.168.10.2`
- Interface: `eth0`

The router was connected directly to the test machine in an isolated environment.

The laboratory network was not used to access or test third-party systems.

---

# 2. Initial Network Reconnaissance

The first stage was to identify network services exposed by the router.

An Nmap scan identified the following relevant ports:

| Port | State | Observation |
|---|---|---|
| 21/tcp | filtered | FTP |
| 22/tcp | filtered | SSH |
| 23/tcp | filtered | Telnet |
| 80/tcp | open | HTTP / `micro_httpd` |
| 443/tcp | open | HTTPS / `micro_httpd` |
| 139/tcp | filtered | NetBIOS |
| 445/tcp | filtered | SMB |

The HTTP service became the primary area of investigation.

---

# 3. Web Server Analysis

The router's web interface was accessible at:


http://192.168.10.1/


The server identified itself as:


micro_httpd


A request to the root page resulted in client-side redirection toward the login interface.

The HTTP service also exhibited unusual behavior for some requests, including responses containing multiple pieces of HTTP/page content concatenated together.

This led to further examination of individual web resources rather than relying exclusively on the browser interface.

---

# 4. Login Interface Analysis

The `login.html` page was inspected to understand how authentication requests were constructed.

The login JavaScript contained:

javascript
function loginApply() {
    with ( document.forms[0] ) {
        if(username.value.length <= 0) {
            alert("Please input the username!");
            return;
        }
        var loc = "login.cgi?" +
                  "username=" + encodeUrl(username.value) +
                  "&psd=" + encodeUrl(password.value);

        var code = 'location="' + loc + '"';
        eval(code);
    }
}


This showed that the browser constructs a request to:


login.cgi?username=<username>&psd=<password>


The credentials are therefore transmitted as URL parameters during the login process.

---

# 5. Unauthenticated Login Request Testing

A direct request was made to:


/login.cgi?username=test&psd=test


The response returned an authentication failure message.

The response also contained:


Invalid Session Key, please try again


A cookie was observed:


Set-Cookie: Name=; path=/


At this stage, the behavior of the authentication and session mechanism was investigated further.

---

# 6. Wireless Configuration Page

The wireless configuration interface was identified as:


/wlcfg.html


A significant observation was made when requesting this page without first performing a normal login through the web interface.

The response contained wireless configuration information despite the absence of a conventional authenticated session.

The page included JavaScript variables representing the current wireless configuration.

For example:

javascript
var ssid = '...';
var enbl = '1';
var auth_mode = 'psk2';


The page also contained a dynamically generated:


sessionKey


This became an important part of the subsequent investigation.



# 7. Session-Key Investigation

Multiple fresh requests to `wlcfg.html` were performed.

Each request produced a different session-key value.

Examples observed during testing included:


951473936
1223856951
1015027739
1772979037
1888588438
1107327564


The changing values suggested that the key was generated dynamically rather than being a static value embedded in the page.

Previously obtained keys were also tested against the state-changing wireless configuration endpoint.

A stale key resulted in:


Invalid Session Key, please try again


This demonstrated that the backend was not simply accepting arbitrary session-key values.

---

# 8. Wireless Configuration JavaScript Analysis

The wireless configuration page contained JavaScript responsible for constructing the configuration request.

The relevant function constructed a URL beginning with:


wlcfg.wl?


The request included parameters such as:


wlSsidIdx
wlEnableHspot
wlEnbl
wlHide
wlAPIsolation
wlSsid
wlCountry
wlRegRev
wlMaxAssoc
wlDisableWme
wlEnableWmf


It also included the guest-network configuration parameters.

The JavaScript eventually appended:


wlSyncNvram=1


followed by:


checksumKey=<checksum>


and:


sessionKey=<session key>


---

# 9. Checksum Analysis

The page referenced the following function:


calcChecksumStr(loc)


The function calculates a checksum by summing the character codes of the supplied string.

Conceptually:


checksum = Σ ord(character)


The checksum was calculated over the request string before the `sessionKey` parameter was appended.

For the controlled SSID-change request using:


HACKED-BY-AZAN1


the independently calculated checksum was:


52171


This allowed the request generated by the browser to be reconstructed for controlled testing.

---

# 10. Controlled Request Reconstruction

The wireless configuration request was reconstructed based on the JavaScript logic.

The request targeted:


/wlcfg.wl


and contained:

* Wireless configuration parameters
* Guest-network parameters
* `wlSyncNvram=1`
* The calculated checksum
* A freshly obtained session key

The exact session token used during the successful experiment is intentionally not published in this repository.

Sensitive authentication/session values should remain in private evidence rather than public GitHub documentation.

---

# 11. Controlled SSID Modification

A fresh session key was obtained from a new request to the wireless configuration page.

The request checksum was independently calculated.

The reconstructed request was then submitted against the isolated laboratory router.

The wireless SSID was changed to:

HACKED-BY-AZAN1


The router returned a response indicating that the wireless subsystem would restart.

Relevant response values included:

javascript
var wlRefresh = '1';
var delayTime = 6;
var tipMsg = 'Restarting Wireless... Click menu in the left panel for manual refresh';


This indicated that the configuration operation had been accepted and that the wireless subsystem was being restarted.

---

# 12. Independent Verification

After allowing the wireless subsystem time to restart, the wireless configuration page was requested again.

The returned JavaScript contained:

javascript
var ssid = 'HACKED-BY-AZAN1'


This independently confirmed that the SSID had been modified on the router.

The result was therefore not simply a client-side display modification.

---

# 13. Persistence Testing

A previous controlled SSID modification was also verified after rebooting the router.

The modified wireless configuration persisted after the reboot.

This demonstrated that the tested configuration change was written to persistent router configuration rather than existing only temporarily in the web application's runtime state.

---

# 14. Important Observations

The research produced several distinct observations.

### Observation 1 — Configuration Content Exposure

The wireless configuration page returned configuration-related information without a conventional authenticated login.

### Observation 2 — Dynamic Session Key

The page exposed a dynamically changing session key.

### Observation 3 — Server-Side Session Validation

Stale session keys were rejected by the wireless configuration endpoint.

### Observation 4 — Fresh-Key Configuration Modification

A freshly obtained session key, combined with the correctly calculated checksum, was accepted by the wireless configuration endpoint during controlled testing.

### Observation 5 — Persistent Configuration Change

The SSID modification was stored persistently and survived a reboot.

---

# 15. What Has Not Yet Been Established

The current research should not be interpreted as proof of unrestricted administrative access.

The following questions remain open:

* Whether every administrative configuration endpoint behaves the same way.
* Whether the same mechanism can modify the administrator password.
* Whether other protected configuration functions can be reached using the same mechanism.
* Whether the exposed session key provides access beyond the tested wireless configuration functionality.
* Whether the behavior corresponds exactly to a previously documented vulnerability.
* Whether the firmware contains additional vulnerabilities unrelated to the web interface.

These questions require separate testing and verification.

---

# 16. Next Phase — Firmware Reverse Engineering

The next stage of the project will move below the web interface and examine the firmware itself.

The objective is to understand how the router implements the functionality observed during the web-interface research.

Planned workflow:

text
Firmware Image
      │
      ▼
File Format Identification
      │
      ▼
Firmware Extraction
      │
      ▼
Filesystem Identification
      │
      ▼
CGI / Backend Analysis
      │
      ▼
Authentication & Session Implementation
      │
      ▼
Configuration Handlers
      │
      ▼
System Services
      │
      ▼
Privilege Boundaries


Areas of interest include:

* Firmware filesystem structure
* CGI binaries
* Authentication handlers
* Session-key generation and validation
* Configuration-management binaries
* Startup scripts
* System services
* Privileged processes
* Local privilege boundaries

All firmware analysis will be performed on copies of the original firmware.

---

# 17. Evidence Handling

Original evidence should be preserved before modification or analysis.

Recommended evidence includes:

* Nmap output
* HTTP request/response captures
* Screenshots
* JavaScript source
* Firmware hashes
* Extracted filesystem hashes
* Research scripts
* Timeline of experiments

Sensitive artifacts should not be committed to the public repository.

Examples of material that should remain private:

text
Passwords
Session tokens
Authentication cookies
Private keys
Configuration backups
Serial numbers
Personal information
Raw captures containing credentials


When useful, hashes and sanitized excerpts can be published instead.

---

# 18. Research Philosophy

This project follows a simple principle:

> Document what was observed, distinguish it from hypotheses, and verify security-impact claims experimentally.

Failed experiments are also valuable because they show how the behavior of the system was determined.

The goal is not simply to obtain a result, but to understand:


What happened?
Why did it happen?
Which component caused it?
Can it be reproduced?
What security boundary was crossed?
What evidence supports the conclusion?


---

# 19. Current Status

**Phase 1 — Reconnaissance:** Complete

**Phase 2 — Web/Application Analysis:** Complete for the currently investigated functionality

**Phase 3 — Controlled Wireless Configuration Testing:** Demonstrated

**Phase 4 — Firmware Reverse Engineering:** Planned

---

## Researcher

**Azan**

Security Research / Cybersecurity
