$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ProjectDir "..\..")
$BuildDir = Join-Path $ProjectDir "build"
$ToolsDir = Join-Path $ProjectDir "tools"
$DistDir = Join-Path $RepoRoot "dist"
$SdkRoot = $env:ANDROID_SDK_ROOT

if (-not $SdkRoot) {
    $SdkRoot = $env:ANDROID_HOME
}
if (-not $SdkRoot) {
    $SdkRoot = Join-Path $env:LOCALAPPDATA "Android\Sdk"
}
if (-not (Test-Path $SdkRoot)) {
    throw "Android SDK not found. Set ANDROID_SDK_ROOT or install Android Studio."
}

$AndroidJar = Join-Path $SdkRoot "platforms\android-35\android.jar"
if (-not (Test-Path $AndroidJar)) {
    $Platform = Get-ChildItem (Join-Path $SdkRoot "platforms") -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $Platform) {
        throw "No Android SDK platforms found under $SdkRoot\platforms."
    }
    $AndroidJar = Join-Path $Platform.FullName "android.jar"
}

$BuildTools = Get-ChildItem (Join-Path $SdkRoot "build-tools") -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "aapt2.exe") } |
    Sort-Object Name -Descending |
    Select-Object -First 1
if (-not $BuildTools) {
    throw "No Android build-tools with aapt2 found."
}

$Aapt2 = Join-Path $BuildTools.FullName "aapt2.exe"
$D8 = Join-Path $BuildTools.FullName "d8.bat"
$Zipalign = Join-Path $BuildTools.FullName "zipalign.exe"
$ApkSigner = Join-Path $BuildTools.FullName "apksigner.bat"

$JavaExe = (Get-Command java -ErrorAction SilentlyContinue).Source
if (-not $JavaExe) {
    $JavaExe = "C:\Program Files\Java\jre1.8.0_491\bin\java.exe"
}
if (-not (Test-Path $JavaExe)) {
    throw "java.exe was not found."
}

$Keytool = Join-Path (Split-Path -Parent $JavaExe) "keytool.exe"
if (-not (Test-Path $Keytool)) {
    $KnownJava = "C:\Program Files\Java\jre1.8.0_491\bin\java.exe"
    $KnownKeytool = "C:\Program Files\Java\jre1.8.0_491\bin\keytool.exe"
    if ((Test-Path $KnownJava) -and (Test-Path $KnownKeytool)) {
        $JavaExe = $KnownJava
        $Keytool = $KnownKeytool
    } else {
        $KeytoolCommand = (Get-Command keytool -ErrorAction SilentlyContinue).Source
        if ($KeytoolCommand -and (Test-Path $KeytoolCommand)) {
            $Keytool = $KeytoolCommand
        } else {
            throw "keytool.exe was not found."
        }
    }
}

Remove-Item -LiteralPath $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $BuildDir, $ToolsDir, $DistDir | Out-Null

$CompiledRes = Join-Path $BuildDir "compiled-res"
$GeneratedDir = Join-Path $BuildDir "generated"
$ClassesDir = Join-Path $BuildDir "classes"
$DexDir = Join-Path $BuildDir "dex"
New-Item -ItemType Directory -Force -Path $CompiledRes, $GeneratedDir, $ClassesDir, $DexDir | Out-Null

Write-Host "Compiling Android resources..."
& $Aapt2 compile --dir (Join-Path $ProjectDir "res") -o $CompiledRes
if ($LASTEXITCODE -ne 0) { throw "aapt2 compile failed." }

$FlatFiles = @(Get-ChildItem -Path $CompiledRes -Recurse -Filter *.flat | ForEach-Object { $_.FullName })
if (-not $FlatFiles) {
    throw "No compiled resources were produced."
}

$UnsignedResourcesApk = Join-Path $BuildDir "resources.apk"
Write-Host "Linking Android resources..."
& $Aapt2 link `
    -o $UnsignedResourcesApk `
    -I $AndroidJar `
    --manifest (Join-Path $ProjectDir "AndroidManifest.xml") `
    --java $GeneratedDir `
    --min-sdk-version 23 `
    --target-sdk-version 35 `
    --version-code 1 `
    --version-name 1.0 `
    $FlatFiles
if ($LASTEXITCODE -ne 0) { throw "aapt2 link failed." }

$SourceFiles = @(
    Get-ChildItem -Path (Join-Path $ProjectDir "src") -Recurse -Filter *.java | ForEach-Object { $_.FullName }
    Get-ChildItem -Path $GeneratedDir -Recurse -Filter *.java | ForEach-Object { $_.FullName }
)
if (-not $SourceFiles) {
    throw "No Java source files found."
}

$Javac = (Get-Command javac -ErrorAction SilentlyContinue).Source
if ($Javac) {
    Write-Host "Compiling Java with javac..."
    & $Javac -source 1.8 -target 1.8 -bootclasspath $AndroidJar -d $ClassesDir $SourceFiles
} else {
    $EcjJar = Join-Path $ToolsDir "ecj-4.6.1.jar"
    if (-not (Test-Path $EcjJar)) {
        Write-Host "Downloading Eclipse Java compiler..."
        $EcjUrl = "https://repo.maven.apache.org/maven2/org/eclipse/jdt/core/compiler/ecj/4.6.1/ecj-4.6.1.jar"
        Invoke-WebRequest -Uri $EcjUrl -OutFile $EcjJar
    }
    Write-Host "Compiling Java with ECJ..."
    & $JavaExe -jar $EcjJar -1.8 -classpath $AndroidJar -d $ClassesDir $SourceFiles
}
if ($LASTEXITCODE -ne 0) { throw "Java compilation failed." }

$ClassFiles = @(Get-ChildItem -Path $ClassesDir -Recurse -Filter *.class | ForEach-Object { $_.FullName })
if (-not $ClassFiles) {
    throw "No class files were produced."
}

Write-Host "Converting classes to dex..."
& $D8 --min-api 23 --lib $AndroidJar --output $DexDir $ClassFiles
if ($LASTEXITCODE -ne 0) { throw "d8 failed." }

$DexFile = Join-Path $DexDir "classes.dex"
if (-not (Test-Path $DexFile)) {
    throw "classes.dex was not produced."
}

$UnsignedDexApk = Join-Path $BuildDir "unsigned-dex.apk"
Copy-Item -LiteralPath $UnsignedResourcesApk -Destination $UnsignedDexApk -Force
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Zip = [System.IO.Compression.ZipFile]::Open($UnsignedDexApk, "Update")
try {
    $Existing = $Zip.GetEntry("classes.dex")
    if ($Existing) {
        $Existing.Delete()
    }
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, $DexFile, "classes.dex") | Out-Null
} finally {
    $Zip.Dispose()
}

$AlignedApk = Join-Path $BuildDir "LightskyAIPro-android-debug-aligned.apk"
Write-Host "Aligning APK..."
& $Zipalign -f 4 $UnsignedDexApk $AlignedApk
if ($LASTEXITCODE -ne 0) { throw "zipalign failed." }

$Keystore = Join-Path $ProjectDir "debug.jks"
if (-not (Test-Path $Keystore)) {
    Write-Host "Creating debug keystore..."
    & $Keytool -genkeypair `
        -keystore $Keystore `
        -storepass android `
        -keypass android `
        -alias androiddebugkey `
        -keyalg RSA `
        -keysize 2048 `
        -validity 10000 `
        -dname "CN=Android Debug,O=Android,C=US"
    if ($LASTEXITCODE -ne 0) { throw "debug keystore creation failed." }
}

$OutputApk = Join-Path $DistDir "LightskyAIPro-android-debug.apk"
Write-Host "Signing APK..."
& $ApkSigner sign `
    --v4-signing-enabled false `
    --ks $Keystore `
    --ks-pass pass:android `
    --key-pass pass:android `
    --out $OutputApk `
    $AlignedApk
if ($LASTEXITCODE -ne 0) { throw "apksigner sign failed." }

Write-Host "Verifying APK signature..."
& $ApkSigner verify --verbose $OutputApk
if ($LASTEXITCODE -ne 0) { throw "apksigner verify failed." }

Write-Host "Created $OutputApk"
