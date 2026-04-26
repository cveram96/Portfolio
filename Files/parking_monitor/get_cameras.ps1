# PowerShell script to list camera names on Windows
Get-PnpDevice -Class Camera | Where-Object { $_.Status -eq "OK" } | Select-Object FriendlyName | ForEach-Object {
    if ($_.FriendlyName) {
        Write-Output $_.FriendlyName
    }
}
