# Macro Loop Automation Tool v1.0 by David Tan

A lightweight Python desktop application for automating repetitive tasks like clicking, hovering, waiting, and capturing screenshots. Includes OCR capabilities to extract text from captured screenshots and save results to CSV.

## Features

- **Left Click**: Automate mouse clicks at specific coordinates
- **Mouseover**: Move the mouse to specific positions without clicking
- **Wait**: Add delays between actions
- **Screenshot**: Capture screen regions and automatically extract text using OCR
- **Loop Control**: Run your macro sequence multiple times
- **Save/Load**: Save and load macro sequences as JSON files
- **CSV Export**: Automatically extract text from screenshots and export to `results.csv`
- **Visual Area Picker**: Interactive tool to select screenshot regions
- **Mouse Position Capture**: Countdown timer to capture your current mouse position

## Prerequisites

- Python 3.8 or higher
- Windows 10/11 (requires `ctypes.windll` for DPI awareness)
- Tesseract OCR engine (optional, required only for screenshot OCR functionality)

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd qa-test
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pyautogui pillow pytesseract ttkbootstrap
```

### 4. Install Tesseract OCR (Optional but Recommended)

Tesseract is required only if you plan to use the **Screenshot** action with OCR text extraction.

1. **Download the installer** from: https://github.com/UB-Mannheim/tesseract/wiki
2. **Run the installer** with default settings (recommended installation path: `C:\Program Files\Tesseract-OCR`)
3. **Verify installation**: Open Command Prompt and run `tesseract --version`

#### Alternative: Set Custom Tesseract Path

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

### Issue: Tesseract not found when running OCR

**Solution**: 
1. Verify Tesseract is installed: Open Command Prompt and run `tesseract --version`
2. If not found, download and install from: https://github.com/UB-Mannheim/tesseract/wiki
3. Update the path in `app.py` line 41 if using a custom installation location

### Issue: Screenshot coordinates are incorrect on high-DPI displays

**Solution**: The app includes automatic DPI awareness fixes. If issues persist, try:
1. Right-click `app.py` → Properties → Compatibility
2. Check "Run this program in compatibility mode for:"
3. Select "Windows 10" and click OK

### Issue: Mouse clicks or movements are offset

**Solution**: This is usually a DPI issue. The app auto-detects DPI, but if problems occur:
1. Ensure your display scaling in Windows is set to 100%
2. Or manually update DPI detection in the code

### Issue: App is blurry on high-DPI displays

**Solution**: The DPI awareness code (lines 34-38) should fix this. If still blurry:
1. Right-click the app → Properties → Compatibility
2. Check "Disable fullscreen optimizations"

### Issue: OCR results are blank or low quality

**Troubleshooting**:
1. Ensure Tesseract OCR is properly installed and in your PATH
2. Check that your screenshot region contains readable text
3. Try increasing the screenshot region size
4. For low-quality screenshots, ensure the source content is clear and readable

## Example Workflow

1. **Create a new macro**: Click "New Loop"
2. **Add actions**: 
   - Click "Get Mouse Pos", move mouse to a button, wait 3 seconds
   - Add left click at that position
   - Add wait 2 seconds
   - Use "Pick Area" to capture a screenshot region
   - Add screenshot action
3. **Set loop count**: Enter "5" to repeat the macro 5 times
4. **Save your macro**: Click "Save Loop" and name it `my-test.json`
5. **Run**: Click "Run Loop" and watch the automation happen
6. **View results**: Check `results.csv` for OCR text from all captured screenshots

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
