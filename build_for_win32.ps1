param (
    [bool]$gpu = 0,
    [bool]$snippets = 0,
    [bool]$render = 0,
    [string]$buildtype = "Release",
    [int]$clean = 0  # Before building, delete the build directory entirely
)

if ($snippets -and !$gpu) {
    $gpu = 1;
    write-host "GPU lib enabled for building snippets."
}

function check_command {
    param([string]$command)
    if ((get-command $command -ea silentlycontinue) -eq $null) {
        return 1;
    }
    return 0;
}

if (check_command("cl") -e 0) {
    ./vcvars2019.ps1
}

# Check prerequisites
$missing = check_command("cmake")
$missing += check_command("ninja")
$missing += check_command("cl")

if ($missing) {
    write-host "Visual Studio 2019 was not found!"
    return;
}

$builddir = "$psscriptroot/build/win32/$buildtype"

if ($clean -ne 0) {
    write-host "-- Cleaning.."
    rm -r -force -ea silentlycontinue $builddir
}

write-host "Building $buildtype to $builddir"
pushd # Store current path

write-host "-- Checking dependency..."
python ./download_external.py $(if ($gpu) { "--gpu" } else { "" }) --config $buildtype

mkdir -ea silentlycontinue $builddir
cd $builddir

cmake ../../../physx -G Ninja `
    -DCMAKE_BUILD_TYPE="$buildtype" `
    -DDISABLE_CUDA_PHYSX="$(if ($gpu) { "No" } else { "Yes" })" `
    -DPX_BUILDSNIPPETS="$(if ($snippets) { "ON" } else { "OFF" })" `
    -DPX_BUILDSNIPPETS_RENDER="$(if ($render) { "ON" } else { "OFF" })"

cmake --build . --config $buildtype --target install

popd # Restore current path

exit $LastExitCode