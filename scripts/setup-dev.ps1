# Function the returns all names of directories that have a dagger.json in them
function Get-All-Modules-Names {
    Get-ChildItem -Recurse -Filter dagger.json | ForEach-Object { $_.Directory } | ForEach-Object { $_.Name }
}

# Function that runs "dagger develop" for each module in the subdirectory of the module
function Invoke-Setup-Dev {
    Get-All-Modules-Names | ForEach-Object { dagger develop --mod $_ }
}

Invoke-Setup-Dev