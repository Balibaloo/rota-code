# Set the power limits of the two cards for one of two uses.
#
# The PSU is an RM850. Both cards at their own maximum is over the line
# under transients. This script moves both limits together.
#
#   show      Report the limits. Needs no elevation.
#   game      3080 at 370 W, Titan at its 150 W floor.
#   work      3080 at 320 W, Titan at 200 W. The inference budget.
#   install   Register the two tasks that let an agent flip the modes.
#
# A set needs administrator rights. A set does not survive a reboot.
#
#   powershell -NoProfile -File probes/gpu_power.ps1 -Mode show
#
# Run `install` once in an elevated shell. After that a plain shell flips
# the limits with no prompt:
#
#   schtasks /run /tn rota-gpu-power-game
#   schtasks /run /tn rota-gpu-power-work
#
param(
  [ValidateSet("show", "game", "work", "install")]
  [string]$Mode = "show"
)

$ErrorActionPreference = "Stop"

# The numeric index is not stable across enumerations. Resolve each card by
# name and address it by UUID.
function Get-Uuid([string]$pattern) {
  $line = (nvidia-smi -L) | Where-Object { $_ -match $pattern } | Select-Object -First 1
  if (-not $line) { throw "no card matches '$pattern' in nvidia-smi -L" }
  if ($line -notmatch "\(UUID: (GPU-[0-9a-f-]+)\)") { throw "no UUID in: $line" }
  return $Matches[1]
}

function Show-Limits {
  nvidia-smi --query-gpu=name,power.limit,power.default_limit,power.max_limit --format=csv
}

function Test-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $me = New-Object Security.Principal.WindowsPrincipal($id)
  return $me.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if ($Mode -eq "show") {
  Show-Limits
  exit 0
}

if (-not (Test-Admin)) {
  Write-Error "mode '$Mode' needs administrator rights; run it in an elevated shell"
  exit 1
}

if ($Mode -eq "install") {
  $self = Join-Path $PSScriptRoot "gpu_power.ps1"
  # The installing user, elevated, not SYSTEM: a task owned by SYSTEM
  # answers `schtasks /run` from a plain shell with "Access is denied"
  # (2026-09-12). A task owned by the user at the highest run level starts
  # from that user's plain shell with no prompt, and runs elevated.
  $who = $env:USERDOMAIN + [char]92 + $env:USERNAME
  $principal = New-ScheduledTaskPrincipal -UserId $who -LogonType Interactive -RunLevel Highest
  foreach ($m in @("game", "work")) {
    $argline = "-NoProfile -ExecutionPolicy Bypass -File `"$self`" -Mode $m"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argline
    Register-ScheduledTask -TaskName "rota-gpu-power-$m" -Action $action `
      -Principal $principal -Description "GPU power limits: $m" -Force | Out-Null
    # The task's own security descriptor decides who may start it, and the
    # default gives the user read alone: `schtasks /run` from a plain shell
    # answered "Access is denied" after the first two installs (2026-09-12).
    # Grant the installing user read and execute, administrators and SYSTEM
    # everything, through the Task Scheduler's own API.
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $sddl = "D:(A;;FA;;;BA)(A;;FA;;;SY)(A;;GRGX;;;$sid)"
    $svc = New-Object -ComObject Schedule.Service
    $svc.Connect()
    $svc.GetFolder([char]92).GetTask("rota-gpu-power-$m").SetSecurityDescriptor($sddl, 0)
    Write-Output "registered rota-gpu-power-$m, runnable by $who"
  }
  exit 0
}

$fast = Get-Uuid "RTX 3080"
$slow = Get-Uuid "TITAN X"

if ($Mode -eq "game") { $fastWatts = 370; $slowWatts = 150 }
else                  { $fastWatts = 320; $slowWatts = 200 }

nvidia-smi -i $fast -pl $fastWatts
nvidia-smi -i $slow -pl $slowWatts

Write-Output "mode=$Mode"
Show-Limits
