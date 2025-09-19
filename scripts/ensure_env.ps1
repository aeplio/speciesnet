param(
    [string]$RequiredEnv = 'speciesnet'
)
if (-not $env:CONDA_DEFAULT_ENV) {
    Write-Error "[ENV GUARD] 未检测到激活的conda环境。请先运行: conda activate $RequiredEnv"; exit 1
}
if ($env:CONDA_DEFAULT_ENV -ne $RequiredEnv) {
    Write-Error "[ENV GUARD] 当前环境 '$env:CONDA_DEFAULT_ENV' != '$RequiredEnv'。请先运行: conda activate $RequiredEnv"; exit 2
}
Write-Host "[ENV GUARD] OK - 当前环境: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
