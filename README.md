# blindzz.py - Blind SQL Injection Enumerator Tool

## Overview

`blindzz.py` is a versatile tool designed to automate blind SQL injection for data enumeration. It aids security researchers, penetration testers, and ethical hackers in extracting sensitive database information such as usernames, passwords, table names, and column names. The tool injects custom payloads into URL parameters, cookies, or headers, offering flexibility for a variety of testing scenarios.

## Features

- **Flexible Injection Points**: Test SQL injection in URL parameters, cookies, or HTTP headers.
- **Customizable Payloads**: Tailor payloads to enumerate different data types, such as usernames, table names, and more.
- **Multithreaded Requests**: Supports concurrent threads to speed up enumeration.
- **Character Set Customization**: Specify a custom character set for brute-forcing enumeration.
- **Proxy Support**: Route requests through a proxy for enhanced anonymity or traffic monitoring.
- **Graceful Interruption**: Handles Ctrl+C interruptions without errors, ensuring a clean shutdown.
- **Output to File**: Option to save extracted data to a specified output file for later analysis.
- **Verbose Mode**: Displays detailed progress and step-by-step feedback during execution.

## Installation

1. **Clone the Repository**  
   First, clone the repository to your local machine:

   ```bash
   git clone https://github.com/S2K7x/blindzz.py.git
   cd blindzz.py
   ```

2. **Install Dependencies**  
   Ensure you have Python 3.6 or later installed. Then, install the required packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

`blindzz.py` requires the following Python libraries:

- `argparse`: For parsing command-line arguments.
- `requests`: For making HTTP requests.
- `colorama`: For colored output in the terminal.
- `concurrent.futures`: For handling multi-threading.
- `logging`: For logging events and errors.
- `signal`: For graceful handling of keyboard interrupts.

## Usage

### Command Syntax

```bash
python blindzz.py -f <config_file> [options]
```

### Command-line Arguments

| Argument                 | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `-f, --file`              | **Required**. Path to the JSON configuration file.                          |
| `-c, --charset`           | Character set for brute-forcing (default: `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`). |
| `-l, --length`            | Maximum length of data to enumerate (default: 20).                          |
| `-v, --verbose`           | Enable verbose output to see detailed progress.                            |
| `-d, --delay`             | Delay between requests in seconds (default: 0).                             |
| `-o, --output-file`       | File to save the extracted data (optional).                                 |
| `-s, --success-condition` | Text in the response indicating a successful payload (default: 'Welcome').  |
| `-t, --threads`           | Number of concurrent threads to use (default: 1).                          |
| `-p, --proxy`             | Proxy URL for routing requests (optional).                                 |
| `--inject-target`         | Specify where to inject the payload (e.g., `url`, `cookies`, or `headers`). |

### Search Type Flags

| Flag   | Description              |
|--------|--------------------------|
| `-T, --table`    | Search for table names.      |
| `-C, --column`   | Search for column names.     |
| `-U, --username` | Search for usernames.       |

### Example Commands

1. **Test URL Parameter Injection**  
   Inject a payload into a URL parameter:

   ```bash
   python blindzz.py -f config.json -s "Welcome" --inject-target url -c abcdefghijklmnopqrstuvwxyz0123456789 -l 15 -t 3 -v
   ```

2. **Test Cookie Injection**  
   Perform injection via cookies:

   ```bash
   python blindzz.py -f config.json --inject-target cookies -C -t 5 -v
   ```

3. **Save Extracted Data to a File**  
   Save the result of a username search to `output.txt`:

   ```bash
   python blindzz.py -f config.json -o output.txt -U
   ```

### Example `config.json`

Here’s an example `config.json` structure to configure the tool:

```json
{
  "url": "https://example.com/vulnerable-page?id=",
  "cookies": {
    "TrackingId": "Q4PdiS2byFXHT8ju",
    "session": "IknMIPNhNO1ohpVN3dfWZK6JNaTJhN5l"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8"
  }
}
```

### How It Works

1. **Payload Construction**: Based on the specified injection target (URL, cookies, or headers), the tool constructs SQL injection payloads.
2. **Request Execution**: Payloads are sent in HTTP requests to the target URL, and the tool monitors the response.
3. **Response Analysis**: It checks the response for the success-condition (e.g., a keyword like "Welcome") to determine if the payload was successful.
4. **Data Extraction**: The tool extracts data one character at a time, progressively building the result for each target (e.g., password, username, table name).
5. **Progress Display**: When verbose mode is enabled, real-time updates are provided to show the characters being tested and found.
6. **Output**: Results can be optionally saved to a file for further analysis.

### Example Workflow

1. **Testing URL Parameter**  
   If testing a URL parameter, the tool will append payloads such as:
   ```
   GET /?id='AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'a' HTTP/2
   ```

2. The tool will analyze the response to check for the presence of the success condition (e.g., "Welcome").

### Handling Interruptions

`blindzz.py` is designed to handle Ctrl+C interruptions gracefully:

- It will clean up resources and stop execution without errors.
- A message will be displayed to confirm the interruption.

### Logging and Debugging

- Logging is enabled to help with debugging and tracking the tool’s operations.
- Use the `-v` flag for verbose output, which shows detailed information about each step, including which characters are being tested.

## Security and Ethics

**Important**: This tool is designed for use in authorized penetration testing and research only. Unauthorized use against systems without explicit permission is illegal and unethical. Always ensure you have written consent from the target system’s owner before using this tool.

## License

Include licensing information here if applicable.

