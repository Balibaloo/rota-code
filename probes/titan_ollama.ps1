# A second Ollama server on the second card, for the register recorder.
#
# The main Ollama (the tray app, port 11434) is pinned to the fast card by
# two user environment variables set once with setx: CUDA_VISIBLE_DEVICES to
# that card's UUID, and OLLAMA_VULKAN to 0. Vulkan discovery ignores the CUDA
# filter and would put models on the other card (2026-09-12). This script
# starts the second server on port 11435 bound to the other card by UUID.
#
#   powershell -File probes/titan_ollama.ps1 [-Gpu GPU-....] [-Port 11435]
#
# Then record on it:  OLLAMA_HOST=http://127.0.0.1:11435 ROTA_L1=1 pytest ...
# `nvidia-smi -L` lists the UUIDs.
param(
    [string]$Gpu = "GPU-dc5a579d-fdda-4035-e8c0-2614a40cf88d",
    [int]$Port = 11435,
    [string]$Log = "$env:TEMP\ollama-titan.log"
,
    [int]$Parallel = 2
)
# One slot: Ollama defaults to two parallel slots and splits num_ctx between
# them, so 12288 became 6146 and the brief fell off every long session
# (finding 79, 2026-09-15: "truncating input prompt" 208 times in the log).
# The Titan X (Maxwell, WDDM) hits the display driver timeout at one slot with
# the full 12288 window: "CUDA error: the launch timed out" on the first
# prompt (2026-09-15 05:46). Two slots, 6146 each, is what it ran all evening;
# the runner flags a prompt over the window. -Parallel 1 for a long-prompt
# record, with the timeout in mind.
$env:OLLAMA_NUM_PARALLEL = "$Parallel"
$env:OLLAMA_VULKAN = "0"
$env:CUDA_VISIBLE_DEVICES = $Gpu
$env:OLLAMA_HOST = "127.0.0.1:$Port"
Start-Process ollama -ArgumentList serve -WindowStyle Hidden -RedirectStandardError $Log -RedirectStandardOutput "$Log.out"
Write-Output "ollama serve on 127.0.0.1:$Port bound to $Gpu, log $Log"
