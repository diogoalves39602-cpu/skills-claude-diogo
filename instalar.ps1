$destino = Join-Path $env:USERPROFILE ".claude\skills"
New-Item -ItemType Directory -Force $destino | Out-Null
Get-ChildItem (Join-Path $PSScriptRoot "skills") -Directory | ForEach-Object {
    Copy-Item $_.FullName -Destination $destino -Recurse -Force
    Write-Host "Instalada: $($_.Name)"
}
Write-Host "`nPronto! Reinicie o Claude para carregar as skills."
