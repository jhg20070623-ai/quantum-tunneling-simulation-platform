param(
    [Parameter(Mandatory = $true)]
    [string]$SourceA,
    [Parameter(Mandatory = $true)]
    [string]$SourceB,
    [Parameter(Mandatory = $true)]
    [string]$OutPptx
)

$ErrorActionPreference = "Stop"
$outDir = Split-Path -Parent $OutPptx
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$app = New-Object -ComObject PowerPoint.Application
$app.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$target = $null

function Replace-SlideFromFile($presentation, [int]$targetIndex, [string]$file, [int]$sourceIndex) {
    [void]$presentation.Slides.InsertFromFile($file, $targetIndex - 1, $sourceIndex, $sourceIndex)
    $presentation.Slides.Item($targetIndex + 1).Delete()
}

try {
    Copy-Item -LiteralPath $SourceB -Destination $OutPptx -Force
    $target = $app.Presentations.Open($OutPptx, $false, $false, $false)

    # Keep B slides 8-11 untouched. Replace B 1-7 with A 1-7, and B 12 with A 9.
    Replace-SlideFromFile $target 12 $SourceA 9
    for ($i = 7; $i -ge 1; $i--) {
        Replace-SlideFromFile $target $i $SourceA $i
    }

    $target.Save()
    Write-Output "saved=$OutPptx"
    Write-Output "slides=$($target.Slides.Count)"
}
finally {
    if ($null -ne $target) { $target.Close() }
    $app.Quit()
}
