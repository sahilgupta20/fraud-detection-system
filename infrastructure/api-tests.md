\# API Test Collection



Replace `https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions` with your actual endpoint URL.



\## Test 1: Low Risk Transaction

\*\*Expected:\*\* APPROVED 

```bash

curl -X POST "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -H "Content-Type: application/json" -d "{\\"amount\\": 500, \\"transaction\_type\\": \\"debit\_card\\", \\"user\_id\\": \\"user123\\", \\"is\_international\\": false, \\"new\_payee\\": false}"

```



\## Test 2: Medium Risk Transaction

\*\*Expected:\*\* REVIEW\_REQUIRED 

```bash

curl -X POST "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -H "Content-Type: application/json" -d "{\\"amount\\": 6000, \\"transaction\_type\\": \\"wire\_transfer\\", \\"user\_id\\": \\"user456\\", \\"is\_international\\": false, \\"new\_payee\\": true}"

```



\## Test 3: High Risk Transaction

\*\*Expected:\*\* BLOCKED 

```bash

curl -X POST "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -H "Content-Type: application/json" -d "{\\"amount\\": 15000, \\"transaction\_type\\": \\"wire\_transfer\\", \\"user\_id\\": \\"user789\\", \\"is\_international\\": true, \\"new\_payee\\": true}"

```



\## PowerShell Test Script

```powershell

\# Test Low Risk

$test1 = @{amount=500; transaction\_type="debit\_card"; is\_international=$false} | ConvertTo-Json

Invoke-RestMethod -Uri "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -Method POST -Body $test1 -ContentType "application/json"



\# Test Medium Risk

$test2 = @{amount=6000; transaction\_type="wire\_transfer"; new\_payee=$true} | ConvertTo-Json

Invoke-RestMethod -Uri "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -Method POST -Body $test2 -ContentType "application/json"



\# Test High Risk

$test3 = @{amount=15000; transaction\_type="wire\_transfer"; is\_international=$true; new\_payee=$true} | ConvertTo-Json

Invoke-RestMethod -Uri "https://rzrdu0u8gh.execute-api.ap-south-1.amazonaws.com/development/transactions" -Method POST -Body $test3 -ContentType "application/json"

```

