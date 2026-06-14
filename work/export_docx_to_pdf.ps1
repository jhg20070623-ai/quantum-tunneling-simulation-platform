$docx = 'C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\fixed_report.docx'
$pdf = 'C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_report\report.pdf'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $pdf) | Out-Null
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open($docx)
    $doc.ExportAsFixedFormat($pdf, 17)
    Write-Output "exported $pdf"
}
finally {
    if ($doc -ne $null) {
        $doc.Close($false)
    }
    if ($word -ne $null) {
        $word.Quit()
    }
}
