
import os
import subprocess


PHYSX_DIR = os.path.join(
    os.path.dirname(__file__),
    "physx/bin/win.x86_64.vc142.mt/release"
)


exclusion = [
    "SnippetConvert.exe",
    "SnippetLoadCollection.exe",
    "SnippetOmniPvd.exe",
    "SnippetVehicle2Customization.exe",
    "SnippetVehicle2DirectDrive.exe",
    "SnippetVehicle2FourWheelDrive.exe",
    "SnippetVehicle2Multithreading.exe",
    "SnippetVehicle2TankDrive.exe",
    "SnippetVehicle2Truck.exe",
]


def is_exe(file):
    file_ext = os.path.splitext(file)[-1]
    return (
        os.access(file, os.X_OK)
        and file_ext.upper() in os.getenv("PATHEXT").split(";")
    )


failed = []
for item in os.listdir(PHYSX_DIR):
    path = os.path.join(PHYSX_DIR, item)
    if item in exclusion or not (item.startswith("Snippet") and is_exe(path)):
        continue

    print("")
    print("=" * 100)
    print("Running " + path)
    popen = subprocess.Popen(path)
    popen.wait()
    if popen.returncode:
        failed.append(item)

print("End.")

if failed:
    print("\nFailed: ")
    for item in failed:
        print(item)
