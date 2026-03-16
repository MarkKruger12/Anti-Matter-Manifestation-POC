@echo off
set "SRC=C:\Users\mkmdk\Book\Anti Matter"
set "DEST=C:\Users\mkmdk\Book\Dirac Sea Pump"

echo --- Populating Dirac Sea Pump Bins ---

:: 1. Core Logic (Timing Sequence)
xcopy "%SRC%\05_Logic_Mapping\*I-Ching*" "%DEST%\01_Core_Logic\" /Y
xcopy "%SRC%\05_Logic_Mapping\Belnap_Kruger.txt" "%DEST%\01_Core_Logic\" /Y

:: 2. Vacuum Geometry (Aperture)
xcopy "%SRC%\03_Geometry\*Tesseract*" "%DEST%\02_Vacuum_Geometry\" /Y
xcopy "%SRC%\03_Geometry\*Lattice*" "%DEST%\02_Vacuum_Geometry\" /Y

:: 3. Magnetic Containment (Workholding)
xcopy "%SRC%\04_Engineering\*XTP*" "%DEST%\03_Magnetic_Containment\" /Y
xcopy "%SRC%\04_Engineering\*X-Point*" "%DEST%\03_Magnetic_Containment\" /Y

:: 4. Dirac Sea Math (The Engine)
xcopy "%SRC%\01_Math\*Dirac*" "%DEST%\04_Dirac_Sea_Math\" /Y
xcopy "%SRC%\01_Math\*Null*" "%DEST%\04_Dirac_Sea_Math\" /Y

echo --- Migration Complete. Trail Established. ---
pause