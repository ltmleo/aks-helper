#!/usr/bin/python3

import os, json, sys, questionary

HOME = os.getenv("HOME", "~")
AKS_HELPER_PATH = os.getenv('AKS_HELPER_PATH', f"{HOME}/.kube")
AKS_HELPER_FILE = os.getenv('AKS_HELPER_FILE', "AzuremanagedClusters.csv")
AKS_CACHE_PATH = os.getenv('AKS_CACHE_PATH', "/tmp")
AKS_CACHE_FILE = os.getenv("AKS_CACHE_FILE", 'aksHelper.json')
SHELL = os.getenv("SHELL", '/usr/bin/zsh')

def _csv_to_json(csv_path):
    aks_clusters = {}
    with open(f"{AKS_HELPER_PATH}/{AKS_HELPER_FILE}", 'r', encoding='utf-8-sig') as file:
        line = file.readline().strip()
        headers = line.split(",")
        headers.pop(-1)
        file_lines = file.readlines()
        for line in file_lines:
            aks = line.rstrip().split(',')
            aks_cluster = {headers[i]: aks[i].replace("\"","") for i in range(len(headers))}
            aks_clusters[aks_cluster["NAME"]] = aks_cluster
    return aks_clusters

def genarate_json(cache_file):
    csv_path = f"{AKS_HELPER_PATH}/{AKS_HELPER_FILE}"
    aks_clusters = _csv_to_json(csv_path)
    with open(cache_file, "w") as file:
        file.write(json.dumps(aks_clusters, indent=4))

def load_json(cache_file):
    with open(cache_file, "r") as file:
        return json.load(file)

def set_subscription(cluster_name):
    os.system(f"az account set --subscription \"{AKS_CLUSTERS[cluster_name]['SUBSCRIPTION']}\"")

def set_kubeconfig(cluster_name, kubeconfig):
    print(f"Seting {kubeconfig}")
    os.system(f"az aks get-credentials --name {cluster_name} --resource-group {AKS_CLUSTERS[cluster_name]['RESOURCE GROUP']} --admin --file {kubeconfig}")
    
def export_kubeconfig(kubeconfig):
    os.system(f"export KUBECONFIG={kubeconfig} && {SHELL}")


def clean_kubeconfig(kubeconfig):
    print("Cleaning kubeconfig")
    os.system(f"rm {kubeconfig}")

def get_options(clusters_list, filter_arg):
    return ["None"] + [cluster for cluster in clusters_list if filter_arg in cluster]
    

def print_help(exit_code):
    print(f"""
{sys.argv[0]} [options]

options:
    --clean-cache: remove json cached file generatade based on AKS csv file
    --help: print help
    <cluster string>: string in cluster name to filter results

How To Use:
    1. Download the csv file on aks page
    2. Put the file (AKS_HELPER_FILE) in a folder (AKS_HELPER_PATH)
    3. Execute the script ({sys.argv[0]}) [options]
    4. Select the desired cluster (If None, the kubeconfig will be cleaned)
    5. Use kubectl

Envarioment Variables:
    AKS_HELPER_PATH: Path to the aks csv file (default: $HOME/.kube)
    AKS_HELPER_FILE: Name of the aks csv file (default: AzuremanagedClusters.csv)
    AKS_CACHE_PATH:  Directory to save the cached json file (default: /tmp)
    AKS_CACHE_FILE: Name to save the cached json file (default: aksHelper.json)
    
""")
    exit(exit_code)
 

if __name__ == "__main__":
    cache_file = f"{AKS_CACHE_PATH}/{AKS_CACHE_FILE}"
    argv = sys.argv[1] if len(sys.argv) > 1 else ""
    filter_arg = argv if "--" not in argv else ""
    if argv == "--help":
        print_help(0)
    if (not os.path.exists(cache_file) or argv == "--clean-cache"):
        genarate_json(cache_file)
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
        set_kubeconfig(cluster_name, kubeconfig)
        export_kubeconfig(kubeconfig)
    elif os.path.exists(kubeconfig):
        export_kubeconfig(kubeconfig)
    else:
        clean_kubeconfig(kubeconfig)