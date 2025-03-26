from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
import pandas as pd

# Azure Data Explorer (Kusto) details
KUSTO_CLUSTER = "https://aznwsdn.kusto.windows.net/"  # Replace with your cluster URL
KUSTO_DATABASE = "aznwmds"  # Replace with your database name

# Use Azure AD authentication (Replace with your credentials)
KCSB = KustoConnectionStringBuilder.with_interactive_login(KUSTO_CLUSTER)

# Initialize Kusto Client
client = KustoClient(KCSB)

# Define KQL query
KQL_QUERY = """
RnmUtilization
| where StartIP !contains ":"
| where FirstPartyUsage startswith "/Scuba"
| summarize arg_max(DateTimeIngested, *) by Region,StartIP,EndIP
| summarize TotalIps=sum(TotalVips), AvailableIps=sum(AvailableVips) by FirstPartyUsage,Region,IsActivated
| where AvailableIps < 4
| order by FirstPartyUsage,Region asc
"""

# Execute the query
try:
    response = client.execute(KUSTO_DATABASE, KQL_QUERY)
    df = dataframe_from_result_table(response.primary_results[0])  # Convert result to Pandas DataFrame
    
    # Display the results
    print(df)

    # Save results to CSV (Optional)
    df.to_csv("kusto_query_results.csv", index=False)
    print("Results saved to kusto_query_results.csv")

except KustoServiceError as e:
    print(f"Error executing KQL query: {e}")
