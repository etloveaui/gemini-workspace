📁 **추천 폴더 이름**  
```
IssueReports/2025-08-08_display-corruption
```

(날짜와 핵심 증상을 포함해 나중에 동일한 유형이 반복되어도 찾기 쉽게 했습니다.)

---

## 🐞 Issue Report – `invoke start` Output Box Corruption

| Item | Value |
|---|---|
| **Title** | CLI output table is visually corrupted after `invoke start` |
| **Severity** | Medium – does not break function, but hurts readability & user trust |
| **Environment** | Windows 11, Python 3.11.4, Invoke 2.2, Rich 13.x |
| **Steps to Reproduce** | 1. Pull latest commit that removed Rich style tags.<br>2. Run `invoke start`.<br>3. Observe the bottom “status” box. |
| **Expected** | Clean, framed table with all status rows aligned. |
| **Actual** | Border characters and cell content are mis-aligned, producing “broken box” effect (see screenshot below). |
| **Root-Cause (tentative)** | After stripping `[bold yellow]...[/]` tags, the raw string length no longer matches the `rich.table` width calculation, causing overflow and line-wrap glitches. |
| **Suggested Fix** | Either:<br>1. Restore **non-styling** padding (`" Staging "` instead of `"Staging"`) to keep original width, or<br>2. Explicitly set `table.min_width` / `max_width` so Rich recalculates layout. |
| **Work-around** | Resize terminal ≥120 cols – corruption less visible. |
| **Files to Touch** | `tasks.py` lines 70 & 73 (table row insertion). |
| **Labels** | `ui`, `rich`, `good-first-issue` |

---

> **Quick patch idea**  
> ```python
> # keep the visual width identical without Rich markup
> table.add_row(" Staging ", task_name)
> ```

Open to PRs if anyone wants to grab this!