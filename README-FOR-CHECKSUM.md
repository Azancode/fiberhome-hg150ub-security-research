# Research Scripts

Small scripts created during analysis of the FiberHome HG150-Ub web application.

## checksum.py

Reimplements the checksum calculation observed in the router's wireless configuration JavaScript.

The observed implementation calculates the checksum by summing the character codes of the request string.

The checksum is calculated before the `sessionKey` parameter is appended.

### Usage

python3 checksum.py
