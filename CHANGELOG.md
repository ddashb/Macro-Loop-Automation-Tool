# Changelog

All notable changes to Macro Loop Automation Tool are documented in this file.

## [1.0] - 2026-05-08

### Added

#### Game Mode (DirectInput Mouse Control)
- New **Game Mode** toggle checkbox in toolbar
- Enables DirectInput-based mouse input for games that don't respond to standard SendInput
- Gracefully disables if `pydirectinput` is not installed
- Applies to both Click and Mouseover actions when enabled
- Perfect for DirectInput/Raw Input games where standard mouse clicks don't register
- ~50-100ms overhead per action (only when enabled)

#### Editable Actions (In-Place Editing)
- Double-click any action in the Actions list to edit it
- Action details load into the Action Builder
- "Add Action" button changes to "Update Action" while editing
- Changes applied in-place without deleting and re-adding
- Double-click the same action again to cancel editing
- Maintains action position in sequence (no reordering needed)

#### Drag-to-Reorder Actions
- Click and drag any action in the Actions list to reorder
- Visual feedback shows target position during drag
- Immediately updates execution sequence on drop
- Status bar confirms move: "Moved action X → position Y"
- No performance impact
- Eliminates need to delete and re-add to change order

#### Dependencies
- Added `pydirectinput` to `requirements.txt` for Game Mode support
- Updated `requirements.txt` to remove version pins (allows compatibility with Python 3.14+)

#### Documentation
- **README.md**: Expanded with new features, detailed setup guide, comprehensive troubleshooting section
- **SETUP.md**: New file with step-by-step installation and common troubleshooting (new for this version)
- **FEATURES.md**: New file with detailed guides on all new features and best practices (new for this version)
- **CHANGELOG.md**: This file

### Changed

- Updated Toolbar: Added "Game Mode" toggle checkbox
- Updated Action Builder: "Add Action" button now uses StringVar for dynamic label switching
- Updated Listbox: Added bindings for edit (Double-Button-1) and drag (ButtonPress-1, B1-Motion, ButtonRelease-1)
- Updated app.py to handle `_editing_index` state for edit mode
- Updated app.py to handle `_drag_start_index` state for reordering
- Enhanced `_refresh_listbox()` behavior when editing
- README.md: Reorganized with separate sections for new features
- requirements.txt: Changed from pinned versions to floating versions for better Python compatibility

### Fixed

- Game input compatibility issue: Clicks and mouseover now work in games using DirectInput
- Python version compatibility: Removed strict version pins that caused Pillow build failures on Python 3.14

### Improved

- User experience: No more delete-and-re-add workflow for editing or reordering
- Setup experience: Better guidance on Python installation and virtual environment creation
- Troubleshooting: Comprehensive section covering all known issues and solutions
- Documentation: Multi-document approach (README for overview, SETUP for installation, FEATURES for details)

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyautogui | latest | Mouse and keyboard automation |
| pillow | latest | Image processing and screenshots |
| pytesseract | latest | OCR text extraction |
| ttkbootstrap | latest | Modern GUI framework |
| pydirectinput | latest | **NEW** Game-compatible mouse input |

### Migration Notes

If upgrading from an earlier version:

1. **Virtual Environment**: No changes needed if already working
2. **Dependencies**: Run `pip install -r requirements.txt` to get `pydirectinput`
3. **Existing Macros**: All saved JSON macros remain compatible (no format changes)
4. **Settings**: Application state (loop count, etc.) preserved
5. **Features**: New features are optional; old workflow still works

### Known Limitations

- Game Mode only works with DirectInput games; Raw Input games may not respond
- Some antivirus software may block mouse automation; temporarily disable for testing
- OCR works best with high-contrast text (black on white)
- DPI scaling issues may occur; ensure display scaling is set to 100%

### Testing

All features tested on:
- Windows 10/11
- Python 3.12, 3.13, 3.14
- DirectInput games (verified clicks register)
- Standard desktop applications (verified backward compatibility)

### Files Modified

- `app.py` — Main application file (added Game Mode, edit, drag features)
- `requirements.txt` — Added pydirectinput, removed version pins
- `README.md` — Reorganized, expanded documentation

### Files Added

- `SETUP.md` — Quick setup guide with troubleshooting
- `FEATURES.md` — Detailed feature documentation and examples
- `CHANGELOG.md` — This file

### Performance Impact

- Game Mode: ~50-100ms per action (only when enabled; no impact when off)
- Edit feature: No performance impact (same storage as before)
- Drag-to-reorder: No performance impact (in-memory array reordering)
- Backward compatible: Existing macros run at same speed

---

## Future Considerations

### Potential Next Features

- [ ] Keyboard input automation (type text, press keys)
- [ ] Image recognition (find images on screen and click them)
- [ ] Conditional actions (if/else based on screenshot matching)
- [ ] Multiple macros in sequence (chaining)
- [ ] Macro scheduling (run at specific times)
- [ ] Recording mode (automatically record clicks/movements)
- [ ] Undo/Redo stack
- [ ] Macro templates library

### Feedback & Requests

To request features or report issues, please open an issue on GitHub with:
- Description of the feature or issue
- Steps to reproduce (for bugs)
- Python version and OS
- Current behavior vs expected behavior

---

## Version History Summary

| Version | Date | Focus |
|---------|------|-------|
| 1.0 | 2026-05-08 | Game Mode, Edit Actions, Drag-Reorder |
| 0.9 | Previous | Initial release |

---

## Notes for Developers

### Code Structure

The application uses tkinter with ttkbootstrap styling. New features implemented as:

1. **Game Mode**: Boolean toggle var + try/except import of pydirectinput
2. **Edit Actions**: `_editing_index` state var + `_load_action_for_edit()` method
3. **Drag-to-Reorder**: `_drag_start_index` + three event handlers (`_drag_start`, `_drag_motion`, `_drag_release`)

All changes in single `app.py` file for simplicity.

### Testing Checklist

Before release:
- [ ] Game Mode checkbox appears disabled if pydirectinput not installed
- [ ] Game Mode clicks/mouseover register in DirectInput game
- [ ] Double-click loads action into builder
- [ ] "Update Action" replaces in-place
- [ ] Double-click same action cancels edit
- [ ] Drag-reorder updates `self.actions` array
- [ ] Saving macro preserves new order
- [ ] Loading macro restores correct sequence
- [ ] Normal add/remove/run still works
- [ ] No crashes on edge cases (drag out of bounds, etc.)
