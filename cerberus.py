import socket as sc
import ssl, argparse
import colorama

# Routine to extract the header into a string.
def strip_header(res: str) -> str:
	i = 0
	header = ""
	while i < len(res) and res[i] != "\r":
		header += res[i].strip("\r") + "\n"
		i += 1
	return header


# Connect to a given hostname with a given port and protocol.
def connect_with_protocol(s: sc.socket, hostname: str, port: int, http_protocol: str) -> sc.socket:
	# HTTPS case. Note that ssl.PROTOCOL_SSLv23 is deprecated, so we use ssl.PROTOCOL_TLS.
	if http_protocol == "HTTPS":
		s = ssl.wrap_socket(s, keyfile=None, certfile=None, 
			server_side=False, cert_reqs=ssl.CERT_NONE, 
			ssl_version=ssl.PROTOCOL_TLS, do_handshake_on_connect=True
		)
		s.connect((hostname, port))
	# HTTP/2 case.
	elif http_protocol == "HTTP/2":
		ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1_2)
		# Declare this socket wants to advertise for h2 (HTTP/2) protocol.
		ssl_context.set_alpn_protocols(["h2"])
		ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
		ssl_context.options |= ssl.OP_NO_COMPRESSION
		s.connect((hostname, port))
		s = ssl_context.wrap_socket(s, server_hostname=hostname)
		# If HTTP2 and the returned protocol is not h2, we can't connect, throw exception.
		if s.selected_alpn_protocol() != "h2":
			raise Exception("Does not support HTTP/2")
	# HTTP/1.1 case. Connect without TLS.
	else:
		s.connect((hostname, port))
	return s


# Construct socket, send request and receive response.
def send_receive(hostname: str, port: int, protocol: tuple, options: tuple) -> list:
	# Set up socket and try to connect
	s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
	s.settimeout(options[0])
	s = connect_with_protocol(s, hostname, port, protocol[2])

	# Contruct request, print to stdout and send its bytes encoded version.
	req = "GET / HTTP/"+protocol[1]+"\r\nHost: "+hostname+"\r\n\r\n"
	if options[3]:
		print(colorama.Fore.GREEN + f"--- Request Header ----\n{req}"+23*"-")
	s.send(req.encode())

	# Decode response, array-ify on newlines.
	res = s.recv(options[1]).decode(errors="ignore").split("\n")
	s.close()
	if res:
		res_header = strip_header(res)
		if options[3]:
			print(f"--- Response Header ---\n{res_header}"+23*"-")
		return res_header.split("\n")
	return []
	

# Send out request, deal with response status codes, and handle errors.
def try_protocol(hostname: str, port: int, protocol: tuple, options: tuple) -> list:
	print(colorama.Fore.CYAN + colorama.Style.BRIGHT
		+ f"{protocol[2]}: Attempting to connect to {protocol[0]}://{hostname}:{port} for {options[0]} seconds...")
	try:
		res_header = send_receive(hostname, port, protocol, options)

		# 200 OK is 💯 OK!
		if "20" in res_header[0]:
			return res_header

		# Follow 300 redirects unless option specifies not to.
		elif "30" in res_header[0] and not options[2]:
			new_hostname = ""
			# Find line that has the location of redirect. Note we purposefully check for "ocation".
			for line in res_header:
				if "ocation:" in line:
					new_hostname = line.split("://")[1][:-1]
					break
			if new_hostname != hostname:
				print(colorama.Fore.RED + colorama.Style.BRIGHT + f"Redirecting to {new_hostname}.")
				res_header = send_receive(new_hostname, port, protocol, options)
			if res_header:
				return res_header

		elif len(res_header) > 0 and protocol[2] == "HTTP/2":
			return res_header

			# Note: Any 400/500 response codes means server refused client connection, therefore unsuccessful.
		raise Exception(f"Does not support {protocol[2]}")
	
	except Exception as e:
		print("[!]",e)
		return []


# Retrieve cookies from the lines of response headers.
def filter_cookies(lines: list):
	print("Cookies:\n=======", end="")
	for line in lines:
		if "cookie" in line.lower():
			print("\n", end="")
			line = line.split(": ")[1:][0]
			for attr in line.split(";"):
				print(f"\n\t{attr}", end="")


if __name__ == "__main__":
	colorama.init(autoreset=True)
	# Parse args.
	parser = argparse.ArgumentParser(
		description="Connect to web server using HTTPS, HTTP/1.1, and HTTP/2. Fetch cookies and analyze HTTP responses.")
	parser.add_argument("target", type=str, 
		help="The URL of the target web server.")
	parser.add_argument("-n", "--noredirect", action="store_true", 
		help="Do not make new requests on redirect URLs.")
	parser.add_argument("-t", "--timeout", default=5.0, type=float, 
		help="Timeout to attempt each HTTP connection.")
	parser.add_argument("-b", "--bytes", default=10000, type=int, 
		help="Maximum bytes to receive from a response.")
	parser.add_argument("-c", "--cookies", action="store_true", 
		help="Specify to fetch basic cookies.")
	parser.add_argument("-v", "--verbose", action="store_true", 
		help="Verbose output.")
	args = parser.parse_args()

	options = (args.timeout, args.bytes, args.noredirect, args.verbose)
	lines = []
	protocols = [
		(443, ("https", "1.1", "HTTPS")),
		(80, ("http", "1.1", "HTTP/1.1")),
		(443, ("http", "2", "HTTP/2"))
	]

	# Try each protocol.
	for p in protocols:
		res = try_protocol(args.target, p[0], p[1], options)
		if len(res) > 0:
			lines += res
			print(f"Supports {p[1][2]}")

	# Retrieve basic cookies of specified.
	if args.cookies:
		filter_cookies(lines)
