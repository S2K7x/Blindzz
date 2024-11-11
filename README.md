

Blind SQL Injection Enumerator Tool

Overview

This tool is designed to automate blind SQL injection for data enumeration. It helps security researchers and penetration testers extract database information, such as passwords, usernames, table names, and column names, through custom payloads sent via HTTP requests. The tool can inject payloads into URL parameters, cookies, or headers, making it adaptable to various testing scenarios.

Features

	•	Flexible Injection Points: Test SQL injection in URL parameters, cookies, or HTTP headers.
	•	Customizable Payloads: Adjust payloads for different data types like passwords, table names, etc.
	•	Multithreaded Requests: Support for concurrent threads to speed up testing.
	•	Character Set Customization: Specify the character set used for brute-forcing.
	•	Proxy Support: Route requests through a proxy for monitoring or anonymity.
	•	Graceful Interruption: Handle Ctrl+C for clean shutdowns.
	•	Output to File: Save results to a specified output file.
	•	Verbose Mode: Get detailed progress updates during execution.

Installation

	1.	Clone the repository:

git clone https://github.com/your-repo/blind-sql-injection-enumerator.git
cd blind-sql-injection-enumerator


	2.	Install dependencies:
Make sure Python 3.6 or later is installed. Install the required packages using pip:

pip install -r requirements.txt



Dependencies

	•	argparse: For command-line argument parsing.
	•	requests: For making HTTP requests.
	•	colorama: For colored terminal text output.
	•	concurrent.futures: For handling multi-threading.
	•	logging: For enhanced debugging.
	•	signal: For handling keyboard interrupts gracefully.

Usage

Command Syntax

python enumerator.py -f <config_file> [options]

Command-line Arguments

	•	-f, --file: (Required) Path to the JSON configuration file.
	•	-c, --charset: Character set for brute-forcing (default: abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789).
	•	-l, --length: Maximum length of data to enumerate (default: 20).
	•	-v, --verbose: Enable verbose output.
	•	-d, --delay: Delay between requests in seconds (default: 0).
	•	-o, --output-file: File to save the extracted data (optional).
	•	-s, --success-condition: Text in the response indicating a successful payload (default: 'Welcome').
	•	-t, --threads: Number of concurrent threads to use (default: 1).
	•	-p, --proxy: Proxy URL for routing requests (optional).
	•	--inject-target: Specify where to inject the payload (url, cookies, headers).

Search Type Flags

	•	-T, --table: Search for table names.
	•	-C, --column: Search for column names.
	•	-U, --username: Search for usernames.

Example Commands

	1.	Test URL Parameter Injection:

python enumerator.py -f config.json -s "Welcome" --inject-target url -c abcdefghijklmnopqrstuvwxyz0123456789 -l 15 -t 3 -v


	2.	Test Cookie Injection:

python enumerator.py -f config.json --inject-target cookies -C -t 5 -v


	3.	Save Extracted Data to a File:

python enumerator.py -f config.json -o output.txt -U



Example config.json

Create a config.json file with the following structure:

{
  "url": "https://example.com/vulnerable-page?id=",
  "cookies": {
    "TrackingId": "Q4PdiS2byFXHT8ju",
    "session": "IknMIPNhNO1ohpVN3dfWZK6JNaTJhN5l"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
  }
}

How It Works

	1.	Payload Construction: The tool builds SQL payloads based on the specified injection target.
	2.	Request Execution: Sends HTTP requests with the payload injected into the specified target.
	3.	Response Analysis: Checks for the presence of the success-condition in the response.
	4.	Data Extraction: Extracts characters one by one, building the full result for each item.
	5.	Progress Display: Outputs real-time information if verbose mode is enabled.
	6.	Output: Optionally saves results to a file for later analysis.

Example Workflow

	•	If testing a URL parameter, the tool appends payloads to the URL:

GET /?id='AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'a HTTP/2


	•	The tool then checks if the response contains the keyword Welcome to confirm success.

Handling Interruptions

The tool is designed to handle Ctrl+C interruptions gracefully:
	•	Cleans up resources and stops execution without errors.
	•	Displays a message indicating user interruption.

Logging and Debugging

	•	Logging is enabled for easier debugging and tracking.
	•	Use the -v flag for detailed output of each step, showing which characters are being tested and found.

Security and Ethics

Important: This tool is intended for use in authorized penetration testing and research. Unauthorized use against systems without permission is illegal and unethical.

License

Include licensing information here if applicable.
