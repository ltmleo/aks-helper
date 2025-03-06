#!/usr/bin/python3

import os, json, sys, questionary
import logging as log

HOME = os.getenv("HOME", "~")
AKS_HELPER_PATH = os.getenv('AKS_HELPER_PATH', f"{HOME}/.kube")
AKS_HELPER_FILE = os.getenv('AKS_HELPER_FILE', "AzuremanagedClusters.csv")
AKS_CACHE_PATH = os.getenv('AKS_CACHE_PATH', "/tmp")
AKS_CACHE_FILE = os.getenv("AKS_CACHE_FILE", 'aksHelper.json')
AKS_SECOND_TENANT_ALIAS = os.getenv("AKS_SECOND_TENANT_ALIAS", 'ti')
SHELL = os.getenv("SHELL", '/usr/bin/zsh')

def _get_log_level():
    return log.DEBUG if "--debug" in sys.argv else log.INFO

def _csv_to_json(csv_path):
    log.debug(f"Reading csv file: {csv_path}")
    aks_clusters = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as file:
        line = file.readline().strip()
        headers = line.split(",")
        headers.pop(-1)
        file_lines = file.readlines()
        for line in file_lines:
            aks = line.rstrip().split(',')
            aks_cluster = {headers[i]: aks[i].replace("\"","") for i in range(len(headers))}
            aks_clusters[aks_cluster["NAME"]] = aks_cluster
    return aks_clusters

def list_aks():
    log.warning("Not works because of the subscription")
    # Not works because of the subscription
    return os.popen(r'az aks list --query "[].{name:name, resourceGroup:resourceGroup, subscriptionId:id}" -o json').read()

def genarate_json(cache_file, csv_path):
    log.debug(f"Generating json file: {cache_file}")
    aks_clusters = _csv_to_json(csv_path)
    with open(cache_file, "w") as file:
        file.write(json.dumps(aks_clusters, indent=4))

def load_json(cache_file):
    log.debug(f"Loading json file: {cache_file}")
    with open(cache_file, "r") as file:
        return json.load(file)

def set_subscription(cluster_name):
    log.debug(f"Setting subscription: {AKS_CLUSTERS[cluster_name]['SUBSCRIPTION']}")
    os.system(f"az account set --subscription \"{AKS_CLUSTERS[cluster_name]['SUBSCRIPTION']}\"")

def set_kubeconfig(cluster_name, kubeconfig, args):
    log.info(f"Seting {kubeconfig}")
    os.system(f"az aks get-credentials --name {cluster_name} --resource-group {AKS_CLUSTERS[cluster_name]['RESOURCE GROUP']} --file {kubeconfig} {args}")
    
def export_kubeconfig(kubeconfig):
    log.debug(f"exporting KUBECONFIG={kubeconfig}")
    os.system(f"export KUBECONFIG={kubeconfig} && {SHELL}")

def clean_kubeconfig(kubeconfig):
    log.info("Cleaning kubeconfig")
    os.system(f"rm {kubeconfig}")

def get_options(clusters_list, filter_arg):
    return ["None"] + [cluster for cluster in clusters_list if filter_arg in cluster]
    

def print_help(exit_code):
    print(f"""
{sys.argv[0]} [options]

options:
    --clean-cache: remove json cached file generatade based on AKS csv file
    --help: print help
    <opt: tenant alias>: Change to AKS_SECOND_TENANT_ALIAS tenant
    <cluster string>: string in cluster name to filter results

How To Use:
    1. Download the csv file on aks page
    2. Put the file (AKS_HELPER_FILE) in a folder (AKS_HELPER_PATH)
    3. Execute the script ({sys.argv[0]}) [options]
    4. Select the desired cluster (If None, the kubeconfig will be cleaned)
    5. Use kubectl, k9s or something else

Envarioment Variables:
    AKS_HELPER_PATH: Path to the aks csv file (default: $HOME/.kube)
    AKS_HELPER_FILE: Name of the aks csv file (default: AzuremanagedClusters.csv)
    AKS_CACHE_PATH:  Directory to save the cached json file (default: /tmp)
    AKS_CACHE_FILE: Name to save the cached json file (default: aksHelper.json)
    AKS_SECOND_TENANT_ALIAS: Alias to use in the second tenant (default: ti)
""")
    exit(exit_code)
 

if __name__ == "__main__":
    log.basicConfig(level=_get_log_level(), format='%(asctime)s - %(levelname)s - %(message)s')
    cache_file = f"{AKS_CACHE_PATH}/{AKS_CACHE_FILE}"
    csv_file = f"{AKS_HELPER_PATH}/{AKS_HELPER_FILE}"
    set_kubeconfig_args = "--admin"
    argv = sys.argv[1] if len(sys.argv) > 1 else ""
    if argv == AKS_SECOND_TENANT_ALIAS:
        cache_file = f"{AKS_CACHE_PATH}/{AKS_SECOND_TENANT_ALIAS}-{AKS_CACHE_FILE}"
        csv_file = f"{AKS_HELPER_PATH}/{AKS_SECOND_TENANT_ALIAS}-{AKS_HELPER_FILE}"
        argv = sys.argv[2] if len(sys.argv) > 2 else ""
    print(cache_file, csv_file)
    filter_arg = argv if "--" not in argv else ""
    if "--admin=false" in sys.argv:
        print("Disabling --admin credentials")
        set_kubeconfig_args = "--public-fqdn"
    if "--help" in sys.argv:
        print_help(0)
    if (not os.path.exists(cache_file) or argv == "--clean-cache"):
        genarate_json(cache_file, csv_file)
    try:
        AKS_CLUSTERS = load_json(cache_file)
    except Exception as e:
        print(f"Error: {e}")
        print_help(1)
    answers = questionary.form(cluster = questionary.select("Select a cluster", choices=get_options(list(AKS_CLUSTERS.keys()), filter_arg))).ask()
    cluster_name = answers["cluster"]
    kubeconfig = f"{AKS_HELPER_PATH}/{cluster_name}.yaml"
    
    if cluster_name != "None" and not os.path.exists(kubeconfig):
        set_subscription(cluster_name)
        set_kubeconfig(cluster_name, kubeconfig, set_kubeconfig_args)
        export_kubeconfig(kubeconfig)
    elif os.path.exists(kubeconfig):
        export_kubeconfig(kubeconfig)
    else:
        clean_kubeconfig(kubeconfig)
