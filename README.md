# Apollo
A simple, lightweight Remote Access Tool written in Python

Apollo is a cross-platform (Windows, Linux, FreeBSD & MacOS) Remote Access Tool for Python 3.4+. Its features are currently very basic but allow for post-exploitation remote code execution as well as obtaining information on the client system and reporting it back to the Command & Control server.

## Features
 * Capability to control multiple clients at once
 * Cross-platform (Windows, Linux, FreeBSD and macOS)
 * AES-256 encrypted C2 with D-H exchange
 * Accepts connection from multiple clients
 * Remote command execution
 * Standard Linux/Unix utilities (cat, ls, pwd, unzip, wget)
 * System survey of remote client - pulling back system details
 * Kill Apollo on the client system and remove all trace of its existence
 * Perform basic port scanning from remote client
 * Clients attempt reconnection if connection to C&C is lost

## Wiki
* [Build a stand-alone executable](https://github.com/apacketofsweets/Apollo/wiki/Build-a-stand-alone-executable)

## Disclaimer
This tool was written for education purposes. My main goal was to achieve a better understanding of Python. 

Apollo can be used in a red-team penetration testing scenario. Apollo should only be used on systems you have express permission to use/interrogate. Accessing a computer system or network without authorisation or explicit permission is illegal. 

You use this tool at your own risk, the author is not liable for any damages.
