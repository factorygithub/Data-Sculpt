import csv
import autogen
import os
from azure.identity import AzureCliCredential
import random
from typing import Annotated, Literal

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

def read_log_file() -> str:
    file_path="C:\\Users\\sumisra\\login_logs.txt"
    with open(file_path, 'r') as file:
        # Read the entire content of the log file and return it as a string
        return file.read()

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
)
engineer = autogen.AssistantAgent(
    name="SOCAnalyst",
    llm_config=gpt4_config,
    system_message="""SOC Analyst. You are a Security Operations Center (SOC) Analyst with expertise in identifying 
    and responding to security threats. Your role is to read the log file and check if any ip address is trying to maliciously login into our system, you should check for ip with brute-force attempt. If you pass any such ip, pass the ip to ITAdministrator to check if those are trusted IP or required to be blocked . You should talk to ITAdministrator only.""",
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
engineer.register_for_llm(name="read_log_file", description="read log file")(read_log_file)
user_proxy.register_for_execution(name="read_log_file")(read_log_file)

groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, admin], 
    messages=[], 
    max_round=10,
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

