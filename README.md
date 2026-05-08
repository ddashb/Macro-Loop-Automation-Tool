# Macro Loop Automation Tool v1.0 by David Tan

A lightweight Python desktop application for automating repetitive tasks like clicking, hovering, waiting, and capturing screenshots. Includes OCR capabilities to extract text from captured screenshots and save results to CSV. Supports game automation with DirectInput mouse controls.

## Features

### Core Automation
- **Left Click**: Automate mouse clicks at specific coordinates
- **Mouseover**: Move the mouse to specific positions without clicking
- **Wait**: Add delays between actions
- **Screenshot**: Capture screen regions and automatically extract text using OCR
- **Loop Control**: Run your macro sequence multiple times
- **Save/Load**: Save and load macro sequences as JSON files
- **CSV Export**: Automatically extract text from screenshots and export to `results.csv`

### Advanced Features
- **Game Mode**: Toggle DirectInput-based mouse control for compatibility with DirectInput/Raw Input games (where standard mouse clicks don't register)
- **Editable Actions**: Double-click any action in the list to edit it in-place without deleting and re-adding
- **Drag-to-Reorder**: Click and drag actions in the list to rearrange execution order
- **Visual Area Picker**: Interactive tool to select screenshot regions
- **Mouse Position Capture**: Countdown timer to capture your current mouse position

## Prerequisites

- **Python 3.8 or higher** (3.12+ recommended; avoid Python 2.7)
- Windows 10/11 (requires `ctypes.windll` for DPI awareness)
- Tesseract OCR engine (optional, required only for screenshot OCR functionality)

## Installation

### Quick Start

#### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd Macro-Loop-Automation-Tool
```

#### 2. Ensure Python 3 is Installed and Available

- If you don't have Python 3 installed, download it from https://www.python.org (3.12 or 3.13 recommended)
- **Important**: During installation, check **"Add Python to PATH"**
- After installation, open a **new** Command Prompt and verify: `python --version` (should show 3.x, not 2.x)

#### 3. Create and Activate Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Note**: Always use `python` (not `python3`) on Windows after activating the venv.

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Run the Application

```bash
python app.py
```

### Game Mode Setup

The **Game Mode** toggle enables DirectInput-based mouse control for games that don't respond to standard SendInput clicks. This requires `pydirectinput`, which is included in `requirements.txt`.

If the Game Mode checkbox appears disabled (grayed out):
- Ensure `pydirectinput` is installed in your venv: `pip install pydirectinput`
- Verify it's in the **project's virtual environment**, not your system Python

### Tesseract OCR Setup (Optional)

Tesseract is required only if you plan to use the **Screenshot** action with OCR text extraction.

1. **Download the installer** from: https://github.com/UB-Mannheim/tesseract/wiki
2. **Run the installer** with default settings (recommended installation path: `C:\Program Files\Tesseract-OCR`)
3. **Verify installation**: Open Command Prompt and run `tesseract --version`

#### Set Custom Tesseract Path

If Tesseract is installed in a non-standard location, edit `app.py` and update line 41:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\path\to\your\tesseract.exe"
```

## Usage

### Starting the Application

```bash
python app.py
```

The GUI will open with these main sections:
- **Toolbar**: New, Save, Load, Run controls
- **Action Builder**: Add and configure actions
- **Actions List**: View and remove added actions

### Building a Macro

#### 1. Add a Left Click Action

1. Select **"Left Click"** from the Action Type dropdown
2. Click **"Get Mouse Pos"** and hover over your target
3. When the countdown reaches zero, your mouse position is captured in the X and Y fields
4. Click **"Add Action"** to add it to your sequence

#### 2. Add a Mouseover Action

1. Select **"Mouseover"** from the dropdown
2. Capture or manually enter the X and Y coordinates
3. Click **"Add Action"**

#### 3. Add a Wait Action

1. Select **"Wait"** from the dropdown
2. Enter the number of seconds to wait
3. Click **"Add Action"**

#### 4. Add a Screenshot Action

1. Select **"Screenshot"** from the dropdown
2. Click **"Pick Area"** to open the interactive region selector
3. Click and drag to select the area you want to capture
4. Press **Escape** to cancel, or release to confirm
5. Click **"Add Action"** to add the screenshot to your sequence

**Note**: Screenshots are saved to `./screenshots/` with sequential numbering (1.png, 2.png, etc.). After all loops complete, OCR is automatically run on all screenshots and results are saved to `results.csv`.

### Managing Your Macro

#### Preview a Position

1. Set X and Y coordinates in the Left Click fields
2. Click **"Preview Pos"** to move your mouse to that location (helpful for testing)

#### Edit an Existing Action

1. **Double-click** any action in the Actions list
2. The action details load into the Action Builder
3. The **"Add Action"** button changes to **"Update Action"**
4. Modify the action values as needed
5. Click **"Update Action"** to save changes in-place
6. **Tip**: Double-click the same action again to cancel editing and return to "Add Action" mode

#### Reorder Actions

1. Click and **drag any action** in the Actions list
2. Drag it to a new position (visual feedback shows the target location)
3. **Release** to confirm the new order
4. The macro executes actions in the new sequence

#### Remove an Action

1. Click on an action in the Actions list to select it
2. Click **"Remove Selected"** to delete it

#### Save Your Macro

1. Click **"Save Loop"** in the toolbar
2. Choose a location and filename (e.g., `my-macro.json`)
3. Your macro is saved with all actions and the current loop count

#### Load a Saved Macro

1. Click **"Load Loop"** in the toolbar
2. Select a previously saved JSON file
3. All actions and settings are restored

### Running Your Macro

1. Set the **Loop Count** in the toolbar (default: 1)
2. Click **"Run Loop"** to start execution
3. The status bar will show progress
4. Click **"Stop"** at any time to halt execution
5. After completion, screenshots are processed with OCR automatically

#### Stop Mechanism

- Press **"Stop"** button to gracefully stop execution
- Move your mouse to the **top-left corner of the screen** for an emergency failsafe stop

### Output Files

After running a macro with screenshots:

- **Screenshots**: Saved in `./screenshots/` as numbered PNG files (1.png, 2.png, etc.)
- **OCR Results**: Saved as `results.csv` with columns:
  - `image_file`: Screenshot filename
  - `extracted_text`: Text extracted from the screenshot via OCR

## Troubleshooting

### Installation & Setup Issues

#### Issue: `ModuleNotFoundError: No module named 'pyautogui'` (or other module)

**Causes**: 
- Using wrong Python interpreter (system Python instead of venv Python)
- Dependencies not installed in the venv

**Solutions**:
1. **Verify venv is activated**: Command Prompt should show `(.venv)` prefix
2. **Use correct Python command**: Use `python` (not `python3`) after activating venv on Windows
3. **Reinstall dependencies**:
   ```bash
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Check installation**: `pip list` should show `pyautogui`, `pillow`, `pydirectinput`, etc.

#### Issue: `No module named venv` when creating virtual environment

**Cause**: Python 2.7 doesn't support venv (it only exists in Python 3.3+)

**Solutions**:
1. **Install Python 3** (3.12 or 3.13 recommended):
   - Download from https://www.python.org
   - **IMPORTANT**: Check "Add Python to PATH" during installation
2. **Verify Python 3 is available**:
   ```bash
   python --version
   ```
   Should show `Python 3.x.x`, not `Python 2.7.x`
3. **Create venv with Python 3**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### Issue: `pip install` fails with "Pillow build failed" or "error getting requirements"

**Cause**: `requirements.txt` has version pins (e.g., `pillow==10.1.0`) that don't have pre-built wheels for your Python version

**Solutions**:
1. **Update `requirements.txt`** to remove version pins:
   ```
   pyautogui
   pillow
   pytesseract
   ttkbootstrap
   pydirectinput
   ```
2. **Then reinstall**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Alternative**: If you must use specific versions:
   ```bash
   pip install --upgrade pip
   pip install --no-cache-dir -r requirements.txt
   ```

### Game Mode Issues

#### Issue: "Game Mode" toggle is disabled (grayed out)

**Cause**: `pydirectinput` is not installed in the venv (it's either not in `requirements.txt` or wasn't installed)

**Solutions**:
1. **Ensure `pydirectinput` is in `requirements.txt`**:
   - File should contain: `pydirectinput` (no version pin)
2. **Install it explicitly**:
   ```bash
   .venv\Scripts\activate
   pip install pydirectinput
   ```
3. **Verify installation**:
   ```bash
   pip list | grep -i directinput
   ```
   Should show `PyDirectInput` in the list

#### Issue: Game Mode is enabled but clicks still don't work in-game

**Possible causes**:
- Some games use even more restrictive input methods than DirectInput
- The game window may not have focus when the macro runs

**Solutions**:
1. **Ensure the game window has focus**: The game must be the active window when "Run Loop" executes
2. **Test with a simple click**: Add a single click action in an empty area, run with Game Mode on, and verify it registers
3. **Check your game's input method**: Some games use Raw Input or custom protocols that even `pydirectinput` can't bypass
4. **Try without Game Mode first**: Verify basic clicks work normally before enabling Game Mode

### Mouse Input & Positioning Issues

#### Issue: Mouse clicks or movements are offset or inaccurate

**Causes**:
- Display scaling (DPI) mismatch
- Window focus issues
- Coordinate capture during screen scaling change

**Solutions**:
1. **Check Windows display scaling**:
   - Windows Settings → Display → Scale
   - Set to 100% for best accuracy
2. **Recapture mouse positions**: Use "Get Mouse Pos" to recapture coordinates
3. **Use Preview Pos before running**: Test click positions with "Preview Pos" to verify
4. **Disable DPI virtualization** (if issue persists):
   - Right-click `app.py` → Properties → Compatibility
   - Check "Change high DPI settings"
   - Check "Override high DPI scaling behavior"

#### Issue: Screenshot coordinates are incorrect on high-DPI displays

**Solution**: The app includes automatic DPI awareness fixes. If issues persist:
1. Right-click `app.py` → Properties → Compatibility
2. Check "Run this program in compatibility mode for:" → Select "Windows 10"
3. Also check "Disable fullscreen optimizations"

### OCR & Screenshot Issues

#### Issue: Tesseract not found when running OCR

**Solution**: 
1. Verify Tesseract is installed: Open Command Prompt and run `tesseract --version`
2. If not found, download and install from: https://github.com/UB-Mannheim/tesseract/wiki
3. Update the path in `app.py` line 41 if using a custom installation location:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\path\to\your\tesseract.exe"
   ```

#### Issue: OCR results are blank or low quality

**Troubleshooting**:
1. Ensure Tesseract OCR is properly installed and in your PATH
2. Check that your screenshot region contains readable text
3. Try increasing the screenshot region size
4. For low-quality screenshots, ensure the source content is clear and readable
5. Verify text is black/dark on light background (OCR works best with high contrast)

### Display & UI Issues

#### Issue: App window is blurry on high-DPI displays

**Solution**: The DPI awareness code should fix this automatically. If still blurry:
1. Right-click `app.py` → Properties → Compatibility
2. Check "Disable fullscreen optimizations"
3. Click "Change high DPI settings" and enable "Override high DPI scaling behavior"

### General Troubleshooting Checklist

If you encounter an unexpected issue:

1. **Restart with fresh venv**:
   ```bash
   rmdir /s /q .venv
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Check Python version**: `python --version` should show 3.8+

3. **Verify all dependencies**: `pip list` should include:
   - pyautogui
   - pillow
   - pytesseract
   - ttkbootstrap
   - pydirectinput

4. **Check file permissions**: Ensure you have write permissions in the project directory for saving macros and screenshots

5. **Disable antivirus temporarily**: Some security software blocks mouse/keyboard automation; test temporarily disabling it

6. **Try on another computer**: If the issue is machine-specific, it may be an OS/hardware compatibility issue

7. **Check for updates**: Ensure you have the latest version from the repository

## Using Game Mode

The **Game Mode** toggle enables DirectInput-based mouse control for games that don't respond to standard mouse input:

1. **Enable Game Mode**: Check the "Game Mode" checkbox in the toolbar (to the right of the Stop button)
   - If disabled (grayed out), see Troubleshooting → Game Mode Issues
2. **Add your actions** as normal (Left Click, Mouseover, etc.)
3. **Run your macro**: Click "Run Loop" with Game Mode enabled
4. **Verify it works**: Test with a simple single-click in an empty area first before adding complex actions

**Note**: Game Mode uses `pydirectinput` which works with most DirectInput games. If clicks still don't register, the game may use Raw Input or custom protocols that require alternative tools.

## Example Workflow

1. **Create a new macro**: Click "New Loop"
2. **Add actions**: 
   - Click "Get Mouse Pos", move mouse to a button, wait 3 seconds
   - Add left click at that position
   - Add wait 2 seconds
   - Use "Pick Area" to capture a screenshot region
   - Add screenshot action
3. **Edit if needed**: Double-click any action to modify it, or drag to reorder
4. **Set loop count**: Enter "5" to repeat the macro 5 times
5. **Save your macro**: Click "Save Loop" and name it `my-test.json`
6. **Run**: Click "Run Loop" and watch the automation happen
7. **View results**: Check `results.csv` for OCR text from all captured screenshots

## Example: Game Macro Workflow

1. **Create a new macro**: Click "New Loop"
2. **Enable Game Mode**: Check the "Game Mode" checkbox
3. **Add actions**:
   - "Get Mouse Pos" to capture the location of an in-game button
   - Add Left Click at that position
   - Add Wait 1 second
   - Add Mouseover to another location
4. **Test with Loop Count = 1**: Click "Run Loop" to verify clicks register in-game
5. **Adjust Game Mode if needed**: If clicks don't work, see Troubleshooting
6. **Increase Loop Count** and run the full macro once confirmed working

## Advanced Tips

- **Batch Processing**: Create multiple macros for different tasks and run them separately
- **Timing**: Use Wait actions to allow pages/applications to load before taking actions
- **Region Selection**: For better OCR results, select regions that contain clear, readable text
- **Testing**: Always test a macro with Loop Count = 1 before running multiple loops
- **Failsafe**: Keep your mouse ready to move to the top-left corner if you need to emergency-stop the macro

## Keyboard Shortcuts

- **Escape**: Cancel area selection during "Pick Area"

## License

This project is provided as-is for testing and automation purposes.

## Support

For issues, suggestions, or feature requests, please open an issue on GitHub.
