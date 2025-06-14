import os
import shutil
import psutil
import platform
import socket
import subprocess
import logging
from typing import Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("windows_cmd_tools.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def run_cmd(command: List[str], capture_output: bool = True) -> Optional[str]:
    """
    Runs a CMD command and returns its output as a string.

    Args:
        command (List[str]): List of command and arguments to execute.
        capture_output (bool): If True, captures and returns command output.

    Returns:
        Optional[str]: Command stdout output or None if error occurred.
    """
    try:
        result = subprocess.run(command, capture_output=capture_output, text=True, check=True)
        # logger.info(f"Successfully ran command: {' '.join(command)}")
        if capture_output:
            return result.stdout.strip()
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command {' '.join(command)}: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return None

# ----------------------- 🗂️ File and Directory Management -----------------------

def list_files(path: str) -> Optional[str]:
    """
    Lists files and folders in a directory.

    Args:
        path (str): Directory path.

    Returns:
        Optional[str]: List of filenames separated by newlines, or None if error.
    """
    try:
        files = os.listdir(path)
        # logger.info(f"Listed files in {path}")
        return "\n".join(files)
    except Exception as e:
        logger.error(f"Error listing files in {path}: {e}")
        return None

def create_file(path: str, content: Optional[str] = None) -> str:
    """
    Creates a new text file and optionally writes string content to it.

    Args:
        path (str): Full path of the file to create.
        content (Optional[str]): Text content to write to the file. If None, creates an empty file.

    Returns:
        str: Success or error message.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            if content is not None:
                f.write(content)
        result = f"File created at {path}{' with content' if content else ''}."
        # logger.info(result)
    except Exception as e:
        result = f"Error creating file at {path}: {e}"
        logger.error(result)
    return result

def get_current_directory() -> str:
    """
    Gets the current working directory.

    Returns:
        str: Current working directory path.
    """
    cwd = os.getcwd()
    # logger.info(f"Current working directory: {cwd}")
    return cwd

def create_folder(path: str) -> None:
    """
    Creates a folder (directory) if it doesn't exist.

    Args:
        path (str): Path of the folder to create.
    """
    try:
        os.makedirs(path, exist_ok=True)
        # logger.info(f"Folder created or already exists at {path}")
    except Exception as e:
        logger.error(f"Error creating folder at {path}: {e}")

# ----------------------- 🧠 Process and System Management -----------------------

def list_processes() -> Optional[str]:
    """
    Lists active processes with PID and memory usage.

    Returns:
        Optional[str]: Process list as a string or None if error.
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024 * 1024)  # Convert bytes to MB
            processes.append(f"PID: {info['pid']}, Name: {info['name']}, Memory: {mem_mb:.2f} MB")
        result = "\n".join(processes)
        # logger.info("Listed active processes")
        return result
    except Exception as e:
        logger.error(f"Error listing processes: {e}")
        return None

def system_info() -> Optional[str]:
    """
    Shows general system information.

    Returns:
        Optional[str]: System information string or None if error.
    """
    try:
        uname = platform.uname()
        info = (
            f"System: {uname.system}\n"
            f"Node Name: {uname.node}\n"
            f"Release: {uname.release}\n"
            f"Version: {uname.version}\n"
            f"Machine: {uname.machine}\n"
            f"Processor: {uname.processor}"
        )
        # logger.info("Retrieved system information")
        return info
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return None

def check_uptime() -> Optional[str]:
    """
    Gets system uptime.

    Returns:
        Optional[str]: Uptime as string or None if error.
    """
    try:
        uptime_seconds = psutil.boot_time()
        import datetime
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(uptime_seconds)
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        # logger.info(f"System uptime: {uptime_str}")
        return uptime_str
    except Exception as e:
        logger.error(f"Error checking uptime: {e}")
        return None

# ----------------------- 🌐 Network and Connection -----------------------

def get_ip_info() -> Optional[str]:
    """
    Shows local IP configuration.

    Returns:
        Optional[str]: IP addresses of all interfaces or None if error.
    """
    try:
        addrs = psutil.net_if_addrs()
        result = []
        for iface, addr_list in addrs.items():
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    result.append(f"{iface}: {addr.address}")
        # logger.info("Retrieved IP information")
        return "\n".join(result)
    except Exception as e:
        logger.error(f"Error getting IP info: {e}")
        return None

def ping_host(host: str, count: int = 4) -> Optional[str]:
    """
    Pings a host and returns latency info.

    Args:
        host (str): Hostname or IP to ping.
        count (int): Number of ping requests to send.

    Returns:
        Optional[str]: Ping command output or None if error.
    """
    try:
        # Using subprocess to ping because Python stdlib doesn't have native ping
        result = subprocess.run(['ping', '-n', str(count), host], capture_output=True, text=True, check=True)
        # logger.info(f"Pinged host {host}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error pinging host {host}: {e}")
        return None

def list_open_ports() -> Optional[str]:
    """
    Lists open ports and connections.

    Returns:
        Optional[str]: Output of netstat or None if error.
    """
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, check=True)
        # logger.info("Listed open ports")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error listing open ports: {e}")
        return None

def check_dns(domain: str) -> Optional[str]:
    """
    Performs DNS lookup for a domain.

    Args:
        domain (str): Domain name to lookup.

    Returns:
        Optional[str]: nslookup output or None if error.
    """
    try:
        result = subprocess.run(['nslookup', domain], capture_output=True, text=True, check=True)
        # logger.info(f"Performed DNS lookup for {domain}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error performing DNS lookup for {domain}: {e}")
        return None

def traceroute_to(host: str) -> Optional[str]:
    """
    Performs traceroute to a host.

    Args:
        host (str): Hostname or IP.

    Returns:
        Optional[str]: Traceroute output or None if error.
    """
    try:
        result = subprocess.run(['tracert', host], capture_output=True, text=True, check=True)
        # logger.info(f"Performed traceroute to {host}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error performing traceroute to {host}: {e}")
        return None

# ----------------------- 🔐 Users and Security -----------------------

def list_users() -> Optional[str]:
    """
    Lists local users.

    Returns:
        Optional[str]: List of users as string or None if error.
    """
    try:
        import pwd  # Note: pwd module is not available on Windows, so fallback to run cmd:
        # But Windows doesn't have pwd; fallback to cmd call for now:
        return run_cmd(['net', 'user'])
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return None

def whoami() -> Optional[str]:
    """
    Shows current username.

    Returns:
        Optional[str]: Current username or None if error.
    """
    try:
        user = os.getlogin()
        # logger.info(f"Current user: {user}")
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None

def check_user_groups() -> Optional[str]:
    """
    Shows groups of the current user.

    Returns:
        Optional[str]: Groups output or None if error.
    """
    try:
        # No direct stdlib method on Windows; fallback to run cmd:
        return run_cmd(['whoami', '/groups'])
    except Exception as e:
        logger.error(f"Error checking user groups: {e}")
        return None

# ----------------------- 🖥️ System and Environment -----------------------

def get_os_version() -> str:
    """
    Returns the operating system version.

    Returns:
        str: OS version string.
    """
    version = platform.platform()
    # logger.info(f"OS version: {version}")
    return version

def get_hostname() -> str:
    """
    Returns the computer's hostname.

    Returns:
        str: Hostname.
    """
    hostname = socket.gethostname()
    # logger.info(f"Hostname: {hostname}")
    return hostname

def list_drives() -> Optional[str]:
    """
    Lists all drives on the system.

    Returns:
        Optional[str]: Drive letters separated by newlines or None if error.
    """
    try:
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{letter}:\\'):
                drives.append(letter + ':')
        # logger.info("Listed drives")
        return "\n".join(drives)
    except Exception as e:
        logger.error(f"Error listing drives: {e}")
        return None

def disk_usage() -> Optional[str]:
    """
    Shows disk usage information for all drives.

    Returns:
        Optional[str]: Disk usage info or None if error.
    """
    try:
        usage_lines = []
        for drive in list_drives().splitlines():
            total, used, free = shutil.disk_usage(drive + "\\")
            usage_lines.append(
                f"Drive {drive} - Total: {total // (1024**3)} GB, Used: {used // (1024**3)} GB, Free: {free // (1024**3)} GB"
            )
        # logger.info("Retrieved disk usage info")
        return "\n".join(usage_lines)
    except Exception as e:
        logger.error(f"Error retrieving disk usage: {e}")
        return None

# ----------------------- 📂 Text File Manipulation -----------------------

def read_file(path: str) -> Optional[str]:
    """
    Reads contents of a text file.

    Args:
        path (str): Path of the file.

    Returns:
        Optional[str]: File contents or None if error.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # logger.info(f"Read file {path}")
        return content
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return None

def find_in_file(path: str, keyword: str) -> Optional[str]:
    """
    Finds lines containing a keyword in a file.

    Args:
        path (str): File path.
        keyword (str): Keyword to search for.

    Returns:
        Optional[str]: Matching lines separated by newlines or None if error.
    """
    try:
        matches = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if keyword in line:
                    matches.append(line.rstrip('\n'))
        # logger.info(f"Found {len(matches)} matches of '{keyword}' in {path}")
        return "\n".join(matches)
    except Exception as e:
        logger.error(f"Error searching in file {path}: {e}")
        return None

# ----------------------- 🛑 Visual Environment Control -----------------------

def open_explorer(path: str) -> bool:
    """
    Opens Windows Explorer at the specified path.

    Args:
        path (str): Path to open.
    Returns:
       bool: True if successful, False otherwise.
    """
    try:
        os.startfile(path)
        # logger.info(f"Opened explorer at {path}")
        return True
    except Exception as e:
        logger.error(f"Error opening explorer at {path}: {e}")
        return False

def open_app(path_to_exe: str) -> bool:
    """
    Opens an application executable.

    Args:
        path_to_exe (str): Path to the executable.
    Returns:
       bool: True if successful, False otherwise.
    """
    try:
        os.startfile(path_to_exe)
        # logger.info(f"Opened application {path_to_exe}")
        return True
    except Exception as e:
        logger.error(f"Error opening application {path_to_exe}: {e}")
        return False

def show_message_box(text: str, title: str) -> bool:
    """
    Shows a Windows message box using PowerShell.

    Args:
        text (str): Message text.
        title (str): Message box title.
    Returns:
       bool: True if successful, False otherwise.
    """
    ps_command = f'& {{Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show(\'{text}\', \'{title}\')}}'
    try:
        subprocess.run(['powershell', '-Command', ps_command], check=True)
        # logger.info(f"Displayed message box: {title} - {text}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error showing message box: {e}")
        return False
