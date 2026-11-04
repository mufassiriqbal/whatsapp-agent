param(
  [string]$From = "923001112222",
  [string]$Text = "How many leave days do I get?",
  [string]$MsgId = "wamid.test1",
  [string]$Signature = $null,
  [string]$Secret = "placeholder-app-secret"
)

$json = @{
  entry = @(@{ changes = @(@{ value = @{ messages = @(@{
    from = $From; id = $MsgId; type = "text"; text = @{ body = $Text }
  }) } }) })
} | ConvertTo-Json -Depth 10 -Compress

$bytes = [Text.Encoding]::UTF8.GetBytes($json)

if (-not $Signature) {
  $hmac = New-Object System.Security.Cryptography.HMACSHA256
  $hmac.Key = [Text.Encoding]::UTF8.GetBytes($Secret)
  $Signature = "sha256=" + (-join ($hmac.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }))
}

try {
     $r = Invoke-WebRequest -Uri http://localhost:8002/webhook -Method Post -Body $bytes -UseBasicParsing `
        -ContentType "application/json" -Headers @{ "X-Hub-Signature-256" = $Signature }
  "Status: $($r.StatusCode)"
} catch {
  "Status: $($_.Exception.Response.StatusCode.value__)"
}
