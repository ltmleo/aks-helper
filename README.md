# aks-helper
Simple python3 script to help setting aks connection with kubectl using az-cli (Cross Subscription)

## Dependencies
- python >= 3.8
- pip >= 22.2.2
- azure-cli = 2.39.0

Execute:
```pip install -r requirements.txt``` 

## options:
- **--clean-cache**: remove json cached file generatade based on AKS csv file
- **--help**: print help

## How To Use:
1. Download the csv file on aks page
2. Put the file (AKS_HELPER_FILE) in a folder (AKS_HELPER_PATH)
3. Execute the script ({sys.argv[0]})
4. Select the desired cluster (If None, the kubeconfig will be cleaned)
5. Use kubectl

## Envarioment Variables:
- **AKS_HELPER_PATH**: Path to the aks csv file (default: $HOME/.kube)
- **AKS_HELPER_FILE**: Name of the aks csv file (default: AzuremanagedClusters.csv)
- **AKS_CACHE_PATH**:  Directory to save the cached json file (default: /tmp)
- **AKS_CACHE_FILE**: Name to save the cached json file (default: aksHelper.json)

## Sugestions

Move it to bin folder:
```sudo cp -rf script.py /usr/bin/aks```

Colaborate improving this script :)
