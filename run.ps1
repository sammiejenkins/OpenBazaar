
$local = Get-Location;
$bin = Join-Path $local "bin"

$pythonDir = $bin + "\python27"
$python = $pythonDir + "\python.exe"

#Update the PATH variable so python will be able to detect openssl
$Env:Path = "$bin\OpenSSL\;$Env:Path"

$startParams = "start"
if($args.Count -gt 0)
{
	$startParams = [string]::join(' ', $args) #$args[0]
}

Start-Process $python -NoNewWindow "-m node.openbazaar $startParams"
