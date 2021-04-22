# Cerberus, the Hound of HTTP

A small and simple command line client built with [sockets](https://docs.python.org/3/library/socket.html) and [ssl](https://docs.python.org/3/library/ssl.html) for the purpose of testing HTTP responses of web servers and learning about the application layer.
<br><br>
In Greek mythology, [Cerberus](https://en.wikipedia.org/wiki/Cerberus) is depicted as a three-headed dog that guards the gates of Hades' Underworld. Of course we can say the three heads refer to the three protocols this tool addresses: HTTP/1.1, HTTP/2, and HTTPS.

## Quick Start
```sh
$ git clone https://github.com/oscarsandford/cerberus.git
$ cd cerberus
```
This program runs on built-in Python libraries but also makes use of [Colorama](https://pypi.org/project/colorama/) for cross-platform ANSI escape sequences. The terminal text colouring increases the readability of the output, especially in verbose mode.
```sh
$ pip install colorama
```
<hr>

## Usage
```
$ python3 cerberus.py -h
usage: cerberus.py [-h] [-n] [-t TIMEOUT] [-b BYTES] [-c] [-v] target

Connect to web server using HTTPS, HTTP/1.1, and HTTP/2. Fetch cookies and
analyze HTTP responses.

positional arguments:
  target                The URL of the target web server.

optional arguments:
  -h, --help            show this help message and exit
  -n, --noredirect      Do not make new requests on redirect URLs.
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout to attempt each HTTP connection.
  -b BYTES, --bytes BYTES
                        Maximum bytes to receive from a response.
  -c, --cookies         Specify to fetch basic cookies.
  -v, --verbose         Verbose output.
```
<hr>

## Examples
```
$ python3 cerberus.py www.google.ca
HTTPS: Attempting to connect to https://www.google.ca:443 for 5.0 seconds...
Supports HTTPS
HTTP/1.1: Attempting to connect to http://www.google.ca:80 for 5.0 seconds...
Supports HTTP/1.1
HTTP/2: Attempting to connect to http://www.google.ca:443 for 5.0 seconds...
Supports HTTP/2
```
```
$ python3 cerberus.py uvic.ca
HTTPS: Attempting to connect to https://uvic.ca:443 for 5.0 seconds...
Redirecting to www.uvic.ca.
Supports HTTPS
HTTP/1.1: Attempting to connect to http://uvic.ca:80 for 5.0 seconds...
Redirecting to www.uvic.ca.
Supports HTTP/1.1
HTTP/2: Attempting to connect to http://uvic.ca:443 for 5.0 seconds...
[!] Does not support HTTP/2
```
