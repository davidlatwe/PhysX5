param (
    [string]$buildtype = "Release",
    [int]$clean = 0  # Before building, delete the build directory entirely
)

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

mkdir -ea silentlycontinue $builddir
cd $builddir

cmake ../../../physx -G Ninja -DCMAKE_BUILD_TYPE="$buildtype"

cmake --build . --config $buildtype --target install

popd # Restore current path

exit $LastExitCode