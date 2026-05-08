# Setup Guide - Macro Loop Automation Tool

## Quick Setup (5 minutes)

### Step 1: Install Python 3

1. Go to https://www.python.org
2. Download **Python 3.12** or **3.13** (not 2.7, not 3.14+ unless you know what you're doing)
3. Run the installer
4. **IMPORTANT**: Check ✓ "Add Python to PATH" before clicking Install
5. Complete the installation
6. **Close and reopen Command Prompt** (to refresh PATH)

### Step 2: Verify Python Installation

Open Command Prompt and run:

```bash
python --version
```

Should show `Python 3.12.x` or `Python 3.13.x` (NOT `Python 2.7.x`)

### Step 3: Navigate to Project Folder

```bash
cd "C:\Users\YourUsername\Documents\GitHub\qa-test"
```

Or wherever you downloaded/cloned the project.

### Step 4: Create Virtual Environment

```bash
python -m venv .venv
```

This creates a `.venv` folder (hidden by default).

### Step 5: Activate Virtual Environment

**Windows Command Prompt:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` at the start of your command prompt line.

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

Wait for it to complete (should show "Successfully installed..." at the end).

### Step 7: Run the Application

```bash
python app.py
```

The GUI window should appear. **Success!**

---

## Troubleshooting

### Problem: `Python is not recognized as an internal or external command`

**Solution**: Python is not in your PATH
1. Uninstall Python completely
2. Reinstall from python.org
3. **VERY IMPORTANT**: Check "Add Python to PATH" during installation
4. Restart Command Prompt
5. Try again: `python --version`

### Problem: `No module named venv`

**Solution**: You're running Python 2.7 (which is too old)
1. Install Python 3.12 or 3.13 from python.org
2. Make sure to check "Add Python to PATH"
3. Open a new Command Prompt
4. Try: `python --version` (should now show Python 3.x)
5. Proceed with venv creation

### Problem: `ModuleNotFoundError: No module named 'pyautogui'`

**Solution**: Venv not activated or dependencies not installed
1. Verify venv is activated: `(.venv)` should appear at the start of your command prompt line
2. If not activated, run: `.venv\Scripts\activate`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Try again: `python app.py`

### Problem: Dependencies installation fails (Pillow build error)

**Solution**: Remove version pins from requirements.txt
1. Open `requirements.txt` in a text editor
2. Replace the entire contents with:
   ```
   pyautogui
   pillow
   pytesseract
   ttkbootstrap
   pydirectinput
   ```
3. Save the file
4. Run: `pip install -r requirements.txt`

### Problem: Game Mode toggle is disabled (grayed out)

**Solution**: pydirectinput not installed in your venv
1. Make sure `.venv` is activated (see `(.venv)` prefix)
2. Run: `pip install pydirectinput`
3. Restart the app: `python app.py`
4. Game Mode toggle should now be enabled

---

## Still Having Issues?

### Check Your Setup:

1. **Verify Python 3 is active**:
   ```bash
   python --version
   ```
   Should show `Python 3.x.x`

2. **Verify venv is activated**:
   ```bash
   pip list
   ```
   Should show `pyautogui`, `pillow`, `pydirectinput`, and other packages

3. **Verify you're in the right folder**:
   ```bash
   dir
   ```
   Should show `app.py`, `requirements.txt`, `.venv` folder, `README.md`

4. **Try a fresh start**:
   ```bash
   .venv\Scripts\deactivate
   rmdir /s /q .venv
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

### If Still Stuck:

1. Check the main **README.md** → Troubleshooting section for detailed solutions
2. Verify all dependencies are properly installed: `pip list`
3. Make sure Windows Defender or antivirus isn't blocking Python/pip
4. Try running Command Prompt as Administrator
5. Ensure you have write permissions in the project folder

---

## For Multiple Computers

If you need to set up on another computer:

1. **Download the project** (ZIP from GitHub or git clone)
2. **Extract** to a folder (e.g., `C:\Users\YourName\Documents\Macro-Tool`)
3. **Follow Steps 1-7 above** starting with Python 3 installation
4. If using downloaded ZIP instead of git clone, make sure `requirements.txt` has no version pins (see "Troubleshooting → Dependencies installation fails")

---

## Command Reference

| Command | What it does |
|---------|-------------|
| `python --version` | Check Python version |
| `python -m venv .venv` | Create virtual environment |
| `.venv\Scripts\activate` | Activate venv (Windows) |
| `pip install -r requirements.txt` | Install all dependencies |
| `pip list` | Show installed packages |
| `pip install pydirectinput` | Install single package |
| `python app.py` | Run the application |
| `.venv\Scripts\deactivate` | Deactivate venv (exit back to system Python) |

---

## What Each Dependency Does

- **pyautogui** — Controls mouse and keyboard
- **pillow** — Processes images and screenshots
- **pytesseract** — Reads text from screenshots (OCR)
- **ttkbootstrap** — Creates the modern GUI
- **pydirectinput** — Game-compatible mouse control (Game Mode feature)
