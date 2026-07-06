---
title: "Stop Doing Things Manually: 5 Scripts That'll Make You Look Like a Genius"
date: 2025-01-27
draft: false
tags: ["automation", "powershell", "bash", "scripts", "sysadmin"]
---

# Stop Doing Things Manually: 5 Scripts That'll Make You Look Like a Genius

Look, I'll be honest with you. Last week I caught myself manually checking disk space on 15 servers. FIFTEEN. Like some kind of caveman clicking through Server Manager while my coffee got cold.

That's when I remembered why I got into this job in the first place - to make computers do the boring stuff so I don't have to. If you're still doing repetitive tasks manually, this post is for you.

## Why Automation Isn't Just for the "Script Kiddies"

I used to think automation was for those developers who live in terminals and drink kombucha. Turns out, it's actually for anyone who's tired of doing the same crap over and over.

Here's what changed my mind:
- I automated disk space checks and caught a runaway log file before it took down our file server
- My boss asked how I "magically knew" about patch status across 50 machines (spoiler: I didn't, my script did)
- I actually left work on time for three weeks straight

## Script 1: Never Check Disk Space Manually Again

This one's my favorite because it literally saved my job once. Our main file server was at 98% capacity and I only knew because my script emailed me at 2 AM.

### Windows Version (PowerShell)

```powershell
# DiskAlert.ps1 - Because clicking through diskmgmt.msc is for chumps
param(
    [string[]]$Servers = @("FILESERVER01", "WEBSERVER01"),
    [int]$WarnAt = 80,
    [int]$PanicAt = 90,
    [string]$EmailTo = "your.email@company.com"
)

Write-Host "Checking disk space because I'm too lazy to do it manually..." -ForegroundColor Green

$alerts = @()
foreach ($server in $Servers) {
    try {
        $disks = Get-WmiObject -ComputerName $server -Class Win32_LogicalDisk -Filter "DriveType=3"
        
        foreach ($disk in $disks) {
            $usedPercent = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)
            
            if ($usedPercent -ge $PanicAt) {
                $alerts += "CRITICAL: $server drive $($disk.DeviceID) is $usedPercent% full!"
                Write-Host "OH CRAP: $server $($disk.DeviceID) is at $usedPercent%" -ForegroundColor Red
            }
            elseif ($usedPercent -ge $WarnAt) {
                $alerts += "WARNING: $server drive $($disk.DeviceID) is $usedPercent% full"
                Write-Host "Heads up: $server $($disk.DeviceID) is at $usedPercent%" -ForegroundColor Yellow
            }
            else {
                Write-Host "OK: $server $($disk.DeviceID) is fine ($usedPercent% used)" -ForegroundColor Green
            }
        }
    }
    catch {
        $alerts += "ERROR: Couldn't check $server - it might be dead"
        Write-Host "Failed to check $server - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Send email if there's bad news
if ($alerts) {
    $body = "Your servers are trying to tell you something:`n`n" + ($alerts -join "`n")
    Send-MailMessage -To $EmailTo -Subject "Disk Space Alert!" -Body $body -SmtpServer "your-mail-server"
}
```

### Linux Version (Bash)

```bash
#!/bin/bash
# disk_alert.sh - For when df -h gets old

WARN_THRESHOLD=80
CRITICAL_THRESHOLD=90
EMAIL="your.email@company.com"
SERVERS=("webserver01" "fileserver01" "dbserver01")

echo "Checking disk space like a responsible adult..."

alerts=""

for server in "${SERVERS[@]}"; do
    echo "Checking $server..."
    
    # SSH and get disk usage
    ssh_result=$(ssh $server "df -h | grep -E '/$|/home|/var' | awk '{print \$5 \" \" \$6}'" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        while IFS= read -r line; do
            usage=$(echo $line | cut -d'%' -f1 | cut -d' ' -f1)
            mount=$(echo $line | cut -d' ' -f2)
            
            if [ "$usage" -ge "$CRITICAL_THRESHOLD" ]; then
                echo "CRITICAL: $server $mount is ${usage}% full!"
                alerts+="CRITICAL: $server $mount is ${usage}% full!\n"
            elif [ "$usage" -ge "$WARN_THRESHOLD" ]; then
                echo "WARNING: $server $mount is ${usage}% full"
                alerts+="WARNING: $server $mount is ${usage}% full\n"
            else
                echo "OK: $server $mount looks good (${usage}% used)"
            fi
        done <<< "$ssh_result"
    else
        echo "ERROR: Can't reach $server - might want to check that"
        alerts+="ERROR: Cannot reach $server\n"
    fi
done

# Send email if we found problems
if [ ! -z "$alerts" ]; then
    echo -e "Disk Space Alert!\n\n$alerts" | mail -s "Disk Space Problems!" $EMAIL
fi
```

**Pro tip**: Set this up to run every morning at 8 AM. That way you know about problems before your users start complaining.

## Script 2: Deploy Software Without Losing Your Mind

Remember when you had to install that security patch on 30 machines? Yeah, me neither - I blocked that trauma out. This script does it for you.

### Windows Version

```powershell
# BulkInstall.ps1 - Mass software deployment for the impatient
param(
    [string[]]$Computers = @("PC001", "PC002", "PC003"),
    [string]$InstallerPath = "\\fileserver\software\important-update.msi",
    [string]$InstallArgs = "/quiet /norestart"
)

Write-Host "About to install stuff on $($Computers.Count) machines. Hold onto your butts..." -ForegroundColor Yellow

$jobs = @()
foreach ($computer in $Computers) {
    Write-Host "Starting install on $computer..."
    
    $job = Start-Job -ScriptBlock {
        param($comp, $installer, $args)
        
        $result = @{Computer = $comp; Success = $false; Message = ""}
        
        try {
            # Test if computer is alive first
            if (Test-Connection $comp -Count 1 -Quiet) {
                # Copy installer locally (faster than running over network)
                $localPath = "\\$comp\c$\temp\installer.msi"
                Copy-Item $installer $localPath -Force
                
                # Run the installer
                $process = Invoke-Command -ComputerName $comp -ScriptBlock {
                    param($path, $arguments)
                    Start-Process "msiexec.exe" -ArgumentList "/i $path $arguments" -Wait -PassThru
                } -ArgumentList "C:\temp\installer.msi", $args
                
                # Clean up
                Remove-Item $localPath -Force -ErrorAction SilentlyContinue
                
                if ($process.ExitCode -eq 0) {
                    $result.Success = $true
                    $result.Message = "Installed successfully"
                } else {
                    $result.Message = "Install failed with exit code $($process.ExitCode)"
                }
            } else {
                $result.Message = "Computer is offline or unreachable"
            }
        }
        catch {
            $result.Message = "Error: $($_.Exception.Message)"
        }
        
        return $result
    } -ArgumentList $computer, $InstallerPath, $InstallArgs
    
    $jobs += $job
}

Write-Host "Waiting for installations to finish (this might take a while)..."
$results = $jobs | Wait-Job | Receive-Job

# Show me the damage
$successful = ($results | Where-Object Success).Count
$failed = $results.Count - $successful

Write-Host "`n=== RESULTS ===" -ForegroundColor Cyan
Write-Host "Successful: $successful" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

$results | Where-Object {-not $_.Success} | ForEach-Object {
    Write-Host "  $($_.Computer): $($_.Message)" -ForegroundColor Red
}
```

### Linux Version

```bash
#!/bin/bash
# bulk_install.sh - Deploy packages without the carpal tunnel

SERVERS=("web01" "web02" "db01" "cache01")
PACKAGE="security-update"

echo "Installing $PACKAGE on ${#SERVERS[@]} servers..."
echo "This is either going to work great or break everything."

successful=0
failed=0

for server in "${SERVERS[@]}"; do
    echo "Installing on $server..."
    
    # Run the install via SSH
    ssh $server "sudo apt update && sudo apt install -y $PACKAGE" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS: $server"
        ((successful++))
    else
        echo "FAILED: $server"
        ((failed++))
    fi
done

echo ""
echo "=== RESULTS ==="
echo "Successful: $successful"
echo "Failed: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "You might want to check the failed ones manually..."
    echo "Or just pretend they don't exist. I won't judge."
fi
```

## Script 3: Patch Status Reports

Your boss wants to know patch status? Your compliance guy is asking questions? This script generates a report that makes you look like you have everything under control.

### Windows Version

```powershell
# PatchReport.ps1 - Making me look competent since 2024
param(
    [string[]]$Computers = (Get-ADComputer -Filter * | Select-Object -ExpandProperty Name),
    [string]$ReportPath = "C:\Reports\PatchStatus_$(Get-Date -Format 'yyyyMMdd').html"
)

Write-Host "Generating patch report for $($Computers.Count) computers..." -ForegroundColor Green
Write-Host "This might take a few minutes. Perfect time for more coffee"

$report = @()
$counter = 0

foreach ($computer in $Computers) {
    $counter++
    Write-Progress -Activity "Checking patches" -Status $computer -PercentComplete (($counter / $Computers.Count) * 100)
    
    try {
        $session = New-PSSession -ComputerName $computer -ErrorAction Stop
        
        $info = Invoke-Command -Session $session -ScriptBlock {
            # Get pending updates
            $updateSession = New-Object -ComObject Microsoft.Update.Session
            $updateSearcher = $updateSession.CreateupdateSearcher()
            $searchResult = $updateSearcher.Search("IsInstalled=0")
            
            # Get last boot time
            $lastBoot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
            $uptime = [math]::Round((Get-Date) - $lastBoot).TotalDays, 1)
            
            return @{
                PendingUpdates = $searchResult.Updates.Count
                CriticalUpdates = ($searchResult.Updates | Where-Object { $_.MsrcSeverity -eq "Critical" }).Count
                LastBoot = $lastBoot
                Uptime = $uptime
            }
        }
        
        Remove-PSSession $session
        
        $status = if ($info.CriticalUpdates -gt 0) { "Critical patches needed" }
                 elseif ($info.PendingUpdates -gt 0) { "Updates available" }
                 elseif ($info.Uptime -gt 30) { "Needs reboot (uptime: $($info.Uptime) days)" }
                 else { "Looking good" }
        
        $report += [PSCustomObject]@{
            Computer = $computer
            Status = $status
            PendingUpdates = $info.PendingUpdates
            CriticalUpdates = $info.CriticalUpdates
            LastBoot = $info.LastBoot.ToString("yyyy-MM-dd")
            UptimeDays = $info.Uptime
        }
    }
    catch {
        $report += [PSCustomObject]@{
            Computer = $computer
            Status = "Offline/Error"
            PendingUpdates = "N/A"
            CriticalUpdates = "N/A"
            LastBoot = "N/A"
            UptimeDays = "N/A"
        }
    }
}

# Generate HTML report
$html = $report | ConvertTo-Html -Title "Patch Status Report" -PreContent "<h2>Patch Status Report - $(Get-Date -Format 'yyyy-MM-dd')</h2>"

$html | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved to: $ReportPath" -ForegroundColor Green

# Open it automatically
Start-Process $ReportPath
```

### Linux Version

```bash
#!/bin/bash
# patch_report.sh - Making Linux admins look organized

SERVERS=("web01" "web02" "db01" "cache01" "mail01")
REPORT_FILE="/tmp/patch_report_$(date +%Y%m%d).html"

echo "Generating patch report for ${#SERVERS[@]} servers..."
echo "Time to look professional!"

# Start HTML file
cat > $REPORT_FILE << EOF
<html>
<head>
    <title>Linux Patch Status Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Linux Patch Status Report</h1>
    <p>Generated: $(date)</p>
    
    <table>
        <tr>
            <th>Server</th>
            <th>Status</th>
            <th>Available Updates</th>
            <th>Security Updates</th>
        </tr>
EOF

for server in "${SERVERS[@]}"; do
    echo "Checking $server..."
    
    # Get update info via SSH
    result=$(ssh $server "
        updates=\$(apt list --upgradable 2>/dev/null | grep -c upgradable)
        security=\$(apt list --upgradable 2>/dev/null | grep -c security)
        echo \"\$updates|\$security\"
    " 2>/dev/null)
    
    if [ ! -z "$result" ]; then
        IFS='|' read -r updates security <<< "$result"
        
        if [ "$security" -gt 0 ]; then
            status="Security updates needed"
        elif [ "$updates" -gt 0 ]; then
            status="Updates available"
        else
            status="Up to date"
        fi
        
        echo "        <tr>" >> $REPORT_FILE
        echo "            <td>$server</td>" >> $REPORT_FILE
        echo "            <td>$status</td>" >> $REPORT_FILE
        echo "            <td>$updates</td>" >> $REPORT_FILE
        echo "            <td>$security</td>" >> $REPORT_FILE
        echo "        </tr>" >> $REPORT_FILE
    else
        echo "        <tr>" >> $REPORT_FILE
        echo "            <td>$server</td>" >> $REPORT_FILE
        echo "            <td>Offline/Error</td>" >> $REPORT_FILE
        echo "            <td>N/A</td>" >> $REPORT_FILE
        echo "            <td>N/A</td>" >> $REPORT_FILE
        echo "        </tr>" >> $REPORT_FILE
    fi
done

# Close HTML
cat >> $REPORT_FILE << 'EOF'
    </table>
</body>
</html>
EOF

echo "Report saved to: $REPORT_FILE"
```

## The Bottom Line

These scripts will save you hours every week once implemented. More importantly, they'll catch problems before users notice them. That's the difference between being reactive and being proactive.

Start with the disk space monitor - it's simple, safe, and immediately useful. Once you see how much time it saves, you'll be hooked on automation.

Remember: the best sysadmins are lazy. We let our scripts do the boring work while we focus on the interesting challenges.

---

*Want more practical automation tips? Subscribe to get notified when I publish new guides like this one.*