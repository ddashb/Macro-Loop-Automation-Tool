# New Features Guide

This document explains the advanced features added to Macro Loop Automation Tool v1.0.

## 1. Game Mode (DirectInput Mouse Control)

### What is Game Mode?

Some games ignore standard mouse input (SendInput) and only respond to DirectInput or Raw Input. **Game Mode** uses `pydirectinput` to send mouse input in a different way that many games accept.

### When to Use Game Mode

- ✓ Clicks don't register in a DirectInput game
- ✓ Mouseover actions don't work in-game
- ✗ Don't use for regular desktop applications (it's slower)

### How to Use

1. **Enable Game Mode**: Check the "Game Mode" checkbox in the toolbar (right side, next to Stop button)
   - Checkbox appears disabled? See Troubleshooting in README.md
2. **Add your actions** normally (Left Click, Mouseover, Wait, Screenshot)
3. **Run the macro** with Game Mode enabled

### Example: Game Macro

```
1. Game Mode: ☑ (checked)
2. Action 1: Left Click at (640, 360) — clicks center of screen
3. Action 2: Wait 1 second
4. Action 3: Mouseover at (600, 300) — moves mouse without clicking
5. Set Loop Count: 5
6. Click Run Loop
```

### Limitations

- Some games use Raw Input or custom input methods that Game Mode can't bypass
- Game Mode works best with DirectInput games (common in older games and some indie games)
- Always test with a simple single-click first before running complex macros

### Performance Impact

- Game Mode is slightly slower (~50-100ms overhead per action)
- Only use when necessary; disable for non-game macros
- If a game works with Game Mode OFF, keep it off for faster execution

---

## 2. Editable Actions (Double-Click to Edit)

### What is It?

Instead of deleting and re-adding actions, double-click any action to edit it in-place. Perfect for tweaking coordinates or values without losing your place in the macro sequence.

### How to Use

1. **Double-click** any action in the Actions list
2. The action details appear in the Action Builder (top section)
3. The **"Add Action"** button changes to **"Update Action"**
4. Modify any values (X, Y coordinates, wait time, etc.)
5. Click **"Update Action"** to save changes
6. The action updates in-place in the list

### Example: Adjusting Click Position

```
Original action: Left Click at (640, 360)
↓
Double-click the action in the list
↓
Change X to 650, Y to 370
↓
Click "Update Action"
↓
Action now: Left Click at (650, 370)
```

### Cancel Editing

- **Double-click the same action again** to cancel editing
- The button reverts to "Add Action"
- No changes are saved

### Tips

- **Quick coordinate adjustment**: Use "Preview Pos" before updating to verify the new location
- **Batch edits**: Edit multiple actions without re-running the macro
- **Safe editing**: Original action isn't removed until you click "Update Action"

---

## 3. Drag-to-Reorder Actions

### What is It?

Click and drag any action in the list to reorder the execution sequence. No need to delete and re-add actions to change their order.

### How to Use

1. **Click and hold** on any action in the Actions list
2. **Drag** up or down to your desired position
3. **Release** the mouse button to confirm the new position
4. The macro executes actions in the new order

### Example: Reordering Macro Steps

```
Original order:
  1. Click button A
  2. Wait 2 seconds
  3. Click button B
  4. Screenshot

↓ (drag step 3 above step 2)

New order:
  1. Click button A
  2. Click button B      ← moved up
  3. Wait 2 seconds      ← moved down
  4. Screenshot
```

### Visual Feedback

- The target position is highlighted as you drag
- The action order updates immediately on release
- Status bar shows: "Moved action X → position Y"

### Tips

- **Test after reordering**: Always verify the new sequence works before running full loops
- **Drag carefully**: Make sure the mouse is over the action you want to drag
- **Quick rearrange**: Much faster than delete+re-add for reorganizing macros

---

## 4. Combined: Edit + Reorder Workflow

### Typical Advanced Workflow

1. **Record initial actions**: Add all actions in any order
2. **Edit for precision**: Double-click actions to fine-tune coordinates
3. **Reorder for logic**: Drag actions to fix execution sequence
4. **Test and refine**: Run with Loop Count = 1, adjust as needed
5. **Save**: Click "Save Loop" to persist changes

### Example: Building a Game Macro

```
Step 1: Add actions roughly
  - Left Click (centered on screen)
  - Mouseover (target location)
  - Screenshot (region)

Step 2: Edit for precision
  - Double-click click action → adjust to exact button position
  - Double-click mouseover → adjust to exact target

Step 3: Reorder if needed
  - Drag screenshot to run first (to get baseline)
  - Reorder click/mouseover as needed

Step 4: Add waits
  - Click "Mouseover" in type dropdown
  - Add "Wait 1 second" between actions
  - Edit existing actions' wait times

Step 5: Test
  - Set Loop Count to 1
  - Enable Game Mode if needed
  - Run and verify
  - Adjust coordinates/waits based on results

Step 6: Save
  - Click "Save Loop"
  - Name it "game-macro-v1.json"
```

### Quick Tips for Efficient Workflow

| Task | Method |
|------|--------|
| Fix a coordinate | Double-click action → change X/Y → "Update Action" |
| Change action order | Click + drag in list → release |
| Add a wait between steps | Insert new action via "Reorder" or edit existing |
| Remove unwanted action | Select action → click "Remove Selected" |
| Test changes | Loop Count = 1, click "Run Loop" |
| Undo all changes | Click "New Loop" (requires re-adding actions) |

---

## Feature Combinations

### Game + Edit Example

```
1. Create game macro with clicks at (640, 360)
2. Test in-game: clicks register but slightly off-center
3. Double-click click action → change to (650, 370)
4. Click "Update Action"
5. Test again with Game Mode enabled
6. If better, save; if not, adjust further
```

### Edit + Reorder Example

```
1. Add 5 actions (click, wait, mouseover, screenshot, click)
2. Realize screenshot should come first
3. Drag screenshot to position 1
4. Double-click click actions to fine-tune coordinates
5. Double-click wait to change duration
6. Run with Loop Count = 1 to verify order
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Escape` | Cancel "Pick Area" (screenshot selection) |
| (none) | Double-click to edit action |
| (none) | Click + drag to reorder action |

---

## Performance Notes

- **Editable actions**: No performance impact; stored same way as before
- **Drag-to-reorder**: No performance impact; just rearranges the list
- **Game Mode**: ~50-100ms slower per action (only when enabled)
- **OCR processing**: Still runs after all loops complete (no change)

---

## Troubleshooting New Features

### Game Mode toggle is disabled

See README.md → Troubleshooting → Game Mode Issues

### Can't edit an action

- Make sure you **double-clicked** (not single-click)
- Button should change to "Update Action" when in edit mode
- If not, try clicking the action first, then double-clicking

### Drag-to-reorder isn't working

- Make sure you're **clicking and holding** before dragging
- Try dragging slowly to different positions
- Release cleanly without dragging off the listbox area

### Edited action looks wrong after updating

- The list refreshes immediately after "Update Action"
- If coordinates seem offset, verify with "Preview Pos"
- Check that you clicked "Update Action" (not "Add Action" which would add a duplicate)

---

## Comparison: Old vs New Workflow

### Old Way (Delete + Re-add)

```
Original: Click at (640, 360)
↓
Select action → "Remove Selected"
↓
"Get Mouse Pos" again
↓
Add action (duplicate now exists)
↓
Remove duplicate
```

### New Way (Edit In-Place)

```
Original: Click at (640, 360)
↓
Double-click action
↓
Change value to (650, 370)
↓
"Update Action"
✓ Done
```

---

## Best Practices

1. **Edit before moving**: Edit coordinates first, then reorder if needed
2. **Test frequently**: Run with Loop Count = 1 after major changes
3. **Save often**: Save after getting a working sequence
4. **Comments in filenames**: Use descriptive names like `game-clicks-v2.json`
5. **Version your macros**: Keep multiple versions of successful macros

---

## Advanced: Macro Templates

Create template macros and reuse them:

1. Build a basic macro (click + wait + click)
2. Save it as `template-basic.json`
3. Open it, edit coordinates, save as `game-specific-v1.json`
4. Repeat with different games, reusing the structure

This way you don't start from scratch every time.
