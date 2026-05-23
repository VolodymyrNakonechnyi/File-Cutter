# FileCutter

Windows GUI utility for splitting one or more `.txt` files into many generated
`generated_text_XXXXXX.txt` files. The source files are not modified.

## Requirements

- Windows 10/11
- Python 3.6 or newer
- Git

## Clone And Run On Windows

```powershell
git clone https://github.com/VolodymyrNakonechnyi/File-Cutter.git
cd File-Cutter

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .

python -m file_configurator
```

## Build Windows EXE

From the project folder:

```powershell
python -m pip install pyinstaller
Remove-Item -Recurse -Force build, dist, FileCutter.spec -ErrorAction SilentlyContinue
pyinstaller --clean --noconfirm --onefile --windowed --name FileCutter --paths src launcher.py
```

The finished Windows executable will be here:

```powershell
.\dist\FileCutter.exe
```

Run it:

```powershell
.\dist\FileCutter.exe
```

The build uses `--windowed`, so the final app opens as a normal Windows GUI app
without a console window.

## Debug EXE Build

If the EXE does not open, build a console version to see the real error:

```powershell
pyinstaller --clean --noconfirm --onefile --console --name FileCutter-debug --paths src launcher.py
.\dist\FileCutter-debug.exe
```

## Usage

1. Select one or more TXT files, or select a folder with TXT files.
2. Select the output folder.
3. Set the average output file size in KB and the standard deviation in KB.
4. Run generation.
5. The app writes `generated_text_000001.txt`, `generated_text_000002.txt`, and so on.

## Tests

```powershell
python -m pytest
```

## Notes

- Do not build the EXE from `src/file_configurator/app.py` directly.
- Build from `launcher.py`, because the application uses package imports.
- Existing `generated_text_*.txt` files in the output folder may be overwritten.
