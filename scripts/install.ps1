# Awesome Plugins for Hermes Agent Installer
# Installs/syncs Hermes plugins into ~/.hermes/plugins, skills into ~/.hermes/skills, and updates config.yaml

$ErrorActionPreference = "Stop"

$HermesRoot = Join-Path $env:USERPROFILE ".hermes"
$PluginsTarget = Join-Path $HermesRoot "plugins"
$SkillsTarget = Join-Path $HermesRoot "skills"
$ConfigFile = Join-Path $HermesRoot "config.yaml"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$SourcePlugins = Join-Path $RepoRoot "plugins"
$SourceSkills = Join-Path $RepoRoot "skills"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Awesome Plugins for Hermes Agent Installer" -ForegroundColor Cyan
Write-Host "  Author: Dr. Eng. Hossam Zein" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ensure target directories
$pluginList = @("cli-bridge", "delegation-bridge", "subscription-bridge")
foreach ($p in $pluginList) {
    $destPlugin = Join-Path $PluginsTarget $p
    if (-not (Test-Path $destPlugin)) {
        New-Item -ItemType Directory -Path $destPlugin -Force | Out-Null
    }
    $destSkill = Join-Path $SkillsTarget $p
    if (-not (Test-Path $destSkill)) {
        New-Item -ItemType Directory -Path $destSkill -Force | Out-Null
    }
}

# 2. Copy Plugin Files
Write-Host "[1/3] Copying plugins to $PluginsTarget..." -ForegroundColor Green
foreach ($p in $pluginList) {
    $src = Join-Path $SourcePlugins $p
    $dst = Join-Path $PluginsTarget $p
    Copy-Item "$src\*" $dst -Recurse -Force
    Write-Host "  + Installed plugin: $p" -ForegroundColor Gray
}

# 3. Copy Skill Files
Write-Host "[2/3] Copying skills to $SkillsTarget..." -ForegroundColor Green
foreach ($p in $pluginList) {
    $srcSkill = Join-Path $SourceSkills "$p\SKILL.md"
    $dstSkill = Join-Path $SkillsTarget "$p\SKILL.md"
    if (Test-Path $srcSkill) {
        Copy-Item $srcSkill $dstSkill -Force
        Write-Host "  + Registered skill: $p" -ForegroundColor Gray
    }
}

# 4. Update config.yaml to enable all 3 plugins & skills
Write-Host "[3/3] Updating $ConfigFile..." -ForegroundColor Green
$configContent = @"
# Hermes Agent Configuration

plugins:
  enabled:
    - cli-bridge
    - delegation-bridge
    - subscription-bridge

skills:
  enabled:
    - cli-bridge
    - delegation-bridge
    - subscription-bridge
    - agent-reach
"@

Set-Content -Path $ConfigFile -Value $configContent -Encoding utf8

Write-Host "Installation complete for Hermes Agent!" -ForegroundColor Green
