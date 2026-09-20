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

try {
    Copy-Item -LiteralPath $SourceB -Destination $OutPptx -Force
    $target = $app.Presentations.Open($OutPptx, $false, $false, $false)

    # Keep B's masters/theme, remove its slides, then reinsert the chosen map.
    for ($i = $target.Slides.Count; $i -ge 1; $i--) {
        $target.Slides.Item($i).Delete()
    }

    # Fusion map: A = stronger visual/story pages, B = more complete/editable detail pages.
    $map = @(
        @{ src = "A"; slide = 1; role = "cover visual" },
        @{ src = "A"; slide = 2; role = "problem framing" },
        @{ src = "A"; slide = 3; role = "physics model" },
        @{ src = "A"; slide = 4; role = "system loop" },
        @{ src = "A"; slide = 5; role = "parameter feature" },
        @{ src = "A"; slide = 6; role = "classic quantum comparison" },
        @{ src = "A"; slide = 7; role = "parameter scan" },
        @{ src = "B"; slide = 8; role = "data and validation" },
        @{ src = "B"; slide = 9; role = "report and export" },
        @{ src = "B"; slide = 10; role = "teaching guide" },
        @{ src = "B"; slide = 11; role = "innovation value" },
        @{ src = "A"; slide = 9; role = "closing visual" }
    )

    foreach ($item in $map) {
        $file = $SourceA
        if ($item.src -eq "A") {
            $file = $SourceA
        } else {
            $file = $SourceB
        }
        [void]$target.Slides.InsertFromFile($file, $target.Slides.Count, $item.slide, $item.slide)
    }

    # Remove accidental empty slides if any.
    for ($i = $target.Slides.Count; $i -ge 1; $i--) {
        $slide = $target.Slides.Item($i)
        if ($slide.Shapes.Count -eq 0) {
            $slide.Delete()
        }
    }

    $target.Save()
    Write-Output "saved=$OutPptx"
    Write-Output "slides=$($target.Slides.Count)"
    foreach ($item in $map) {
        Write-Output "$($item.src)$($item.slide): $($item.role)"
    }
}
finally {
    if ($null -ne $target) { $target.Close() }
    $app.Quit()
}
