import csv
import autogen
import os
from azure.identity import AzureCliCredential
import random
import re
import time
from datetime import datetime, timedelta
from typing import Annotated, Literal
from typing import List

# List of sample users and IP addresses for the logs
users = ["admin", "user1", "user2", "guest", "root", "jdoe"]
ips = ["194.87.3.22", "192.168.1.5", "203.0.113.7", "198.51.100.3", "10.0.0.1", "172.16.0.10"]
status_options = ["FAILED", "SUCCESS"]
 
# Generate log lines
def generate_log_line(user, ip, status, timestamp):
    return f"{timestamp} INFO User login attempt: user={user} ip={ip} status={status}"
 
# Simulate login attempts with random behaviors
def generate_logs(num_logs):
    logs = []
    start_time = datetime(2025, 3, 26, 8, 0, 0)
    current_time = start_time
 
    for _ in range(num_logs):
        user = random.choice(users)
        ip = random.choice(ips)
        status = random.choice(status_options)
       
        # Mimic failed login attempts followed by a success (with some randomization)
        if status == "FAILED":
            # Simulate 2-5 failed attempts before a success
            failed_attempts = random.randint(2, 5)
            for _ in range(failed_attempts):
                logs.append(generate_log_line(user, ip, "FAILED", current_time))
                current_time += timedelta(seconds=1)
 
            # After a few failed attempts, allow a success
            logs.append(generate_log_line(user, ip, "SUCCESS", current_time))
            current_time += timedelta(seconds=1)
        else:
            # Random single successful login
            logs.append(generate_log_line(user, ip, "SUCCESS", current_time))
            current_time += timedelta(seconds=1)
 
        # Occasionally simulate brute-force attempts
        if random.random() < 0.01:  # About 1% chance for brute-force detection
            brute_force_ip = random.choice(ips)
            failed_attempts = random.randint(50, 100)  # High number of failed attempts
            for _ in range(failed_attempts):
                logs.append(generate_log_line(user, brute_force_ip, "FAILED", current_time))
                current_time += timedelta(seconds=1)
            logs.append(f"{current_time} WARNING Brute-force login attempt detected: {failed_attempts}+ failed login attempts from IP {brute_force_ip}")
            current_time += timedelta(seconds=1)
 
        # Randomly increase timestamp for next log (mimicking real-world use)
        current_time += timedelta(seconds=random.randint(1, 5))
 
    return logs
 
# Write the logs to a file
def write_logs_to_file(num_logs, file_path):
    logs = generate_logs(num_logs)
    with open(file_path, "w") as file:
        for log in logs:
            file.write(log + "\n")

# Function that checks files for the bad IPS and Good IPs
def check_ip_trust(ip_address: str) -> str:
    # Check if IP exists in trusted IPs file
    trusted_found = False
    try:
        # Get the absolute path to the trustedIPs.csv file
        trusted_file_path = "C:\\Users\\sumisra\\OneDrive - Microsoft\\desktop\\python\\user.csv" # Define the file path here
        
        with open(trusted_file_path, 'r') as trusted_file:
            csv_reader = csv.reader(trusted_file)
            for row in csv_reader:
                #print(row)
                if ip_address in row:
                    trusted_found = True
                    break
        
        if trusted_found:
            return "It's a trusted IP"
        else:
            # Add to blacklist if not present
            with open('IPblacklist.csv', 'a', newline='') as blacklist_file:
                csv_writer = csv.writer(blacklist_file)
                csv_writer.writerow([ip_address])
            return "IP added to blacklist"
    
    except FileNotFoundError:
        return "Error: Required CSV files not found"
    except Exception as e:
        return f"Error: {str(e)}"

def read_last_n_lines(file_path: str, n: int) -> List[str]:
    """Reads the last 'n' lines from the log file."""
    with open(file_path, 'r') as file:
        # Read all lines and get the last 'n' lines
        lines = file.readlines()
        return lines[-n:]
 
def get_ips_with_failed_or_brute_force() -> str:
    file_path="C:\\Users\\sumisra\\login_logs.txt"
    n=10
    write_logs_to_file(n, file_path)
    """Reads the last 'n' log lines and returns a list of IPs with failed attempts or brute-force attempts."""
    logs = read_last_n_lines(file_path, n)
    ip_failed_attempts = {}
    brute_force_ips = set()
   
    # Regular expression for matching standard log attempts
    login_pattern = re.compile(r'INFO User login attempt: user=\S+ ip=(\S+) status=FAILED')
   
    # Check for failed attempts and brute-force warnings
    for line in logs:
        # Check for failed login attempts
        match = login_pattern.search(line)
        if match:
            ip = match.group(1)
            if ip in ip_failed_attempts:
                ip_failed_attempts[ip] += 1
            else:
                ip_failed_attempts[ip] = 1
 
        # Check for brute-force warnings
        if "WARNING Brute-force login attempt detected" in line:
            match_warning = re.match(r'.*WARNING Brute-force login attempt detected: \d+\+ failed login attempts from IP (\S+)', line)
            if match_warning:
                brute_force_ips.add(match_warning.group(1))
   
    # Collect the IPs with more than 1 failed attempt or brute-force attempts
    result_ips = set(ip for ip, count in ip_failed_attempts.items() if count > 1)
    result_ips.update(brute_force_ips)

    return list(result_ips)[0] if result_ips else None
    
# Define the AI Agent using AutoGen
gpt4_config = {
    "cache_seed": 42,  # Change the cache_seed for different trials
    "temperature": 0,
        "config_list": [
        {
            "model": "gpt-4o",  # Ensure you're using the correct model
            "api_key": "",# Replace with actual API key
            "base_url": "https://datasclupt.openai.azure.com",
            "api_version": "2024-02-15-preview",
            "api_type": "azure"
        }
    ],
    "timeout": 120
}

user_proxy = autogen.UserProxyAgent(
    name="CuriousObserver",
    human_input_mode="NEVER",
    system_message="A human. Interact with the SOC Analyst to discuss the suspicous logins.",
    code_execution_config=False,
    default_auto_reply="""Hi Soc Analyst, can you check if our Network is being attacked by any IP??""",
)
engineer = autogen.AssistantAgent(
    name="SOCAnalyst",
    llm_config=gpt4_config,
    system_message="""SOC Analyst. You are a Security Operations Center (SOC) Analyst with expertise in identifying and responding to security threats. Your role is to get IPs with failed or brute force attemps for ITAdministrator to check if those are trusted IP or required to be blocked .""",
)

admin = autogen.AssistantAgent(
    name="ITAdministrator",
    llm_config=gpt4_config,
    system_message="""IT Administrator. You are responsible for checking trusted IPs and if they are not trusted then blocking them.
""",
)
'''
def state_transition(last_speaker, groupchat):
    messages = groupchat.messages
    
    if last_speaker is engineer:
        return user_proxy
    elif last_speaker is admin:
        return user_proxy
    elif last_speaker is user_proxy:
        last_message = messages[-1]["content"].lower()
        if "blocked" in last_message or "trusted" in last_message:
            return None
'''

# Register the tool signature with the admin agent.
admin.register_for_llm(name="check_ip_trust", description="Check the suspicious IP login alerts based on detected anomalies")(check_ip_trust)
user_proxy.register_for_execution(name="check_ip_trust")(check_ip_trust)

# Register the tool signature with the admin agent.
engineer.register_for_llm(name="get_ips_with_failed_or_brute_force", description="get ips with failed or brute force ")(get_ips_with_failed_or_brute_force)
user_proxy.register_for_execution(name="get_ips_with_failed_or_brute_force")(get_ips_with_failed_or_brute_force)

groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, admin], 
    messages=[], 
    max_round=30,
    #speaker_selection_method=state_transition,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

# Print initial message
print("Initial message from CuriousObserver:")
response = user_proxy.initiate_chat(
    manager,
    message="""
Hi Soc Analyst, can you check if our Network is being attacked by any IP??
"""
)

