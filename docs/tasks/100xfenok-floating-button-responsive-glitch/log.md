# Task: 100xFenok Floating Button Responsive Glitch Fix

## Problem Description
The floating "hamburger" menu button in the 100xFenok application (identified as `.combined-floating-menu`'s `main-toggle-btn`) exhibits a responsive layout glitch. When the screen size exceeds a certain threshold (likely the `lg` breakpoint), the button appears to go "out of frame" or is partially cut off, before eventually disappearing as intended for larger screens.

## Visual Analysis (from `abnormal.jpg` and `normal.jpg`)
*   **`abnormal.jpg`**: Shows the blue circular "hamburger" menu button in the bottom-right corner partially cut off and positioned incorrectly, suggesting it's outside its intended bounds or the viewport.
*   **`normal.jpg`**: Shows the application's main content, but the specific button in question is not visible, implying it's either hidden or not present on that particular screen/context. (Note: The `normal.jpg` provided was of a different section of the app, not directly showing the button in its normal state, but the issue is about its abnormal state).

## Code Analysis

### `index.html`
*   Defines the main page structure with a `frame-container` (flex column), `nav`, `iframe` (`content-frame`), and a `footer`.
*   Links `nav.css` and uses Tailwind CSS.
*   Contains an inline `<style>` block, but no `position: fixed` rules for the button.
*   The `footer` contains a `footer-share-btn` which is a text button, distinct from the circular icon button in `abnormal.jpg`.

### `nav.css`
*   Defines `.combined-floating-menu` with `position: fixed; bottom: 20px; right: 20px; z-index: 1000;`. This confirms the button's fixed positioning relative to the viewport.
*   Contains styles for the `main-toggle-btn` (the blue circular button with hamburger icon).
*   No direct CSS rules for the `enhanced-simple-footer` or `footer-share-btn` that would cause overflow.

### `global.css`
*   Dynamically loaded by `loadNav.js`.
*   Contains general CSS resets, font settings, utility classes, and mobile optimizations.
*   Does **not** contain any `position: fixed` or `absolute` declarations directly affecting the button or footer, nor specific media queries that would cause this layout issue.

### `nav.html`
*   Contains the HTML structure for the `div.combined-floating-menu`, including the `main-toggle-btn`.
*   Crucially, `div.combined-floating-menu` has the Tailwind CSS class `lg:hidden`. This means the floating menu is **intended to be hidden on large screens and above**.

### `loadNav.js`
*   Dynamically loads `global.css` and `nav.html`.
*   Injects the content of `nav.html` (including the floating menu) into the `#nav` container.
*   Does not directly manipulate the button's position.

### `loadPage.js`
*   Responsible for loading content into the `iframe`.
*   Does not directly manipulate the button's position.

## Hypothesis on Cause
The bug is likely a **responsive layout glitch** occurring during the transition to larger screen sizes (at the `lg` breakpoint) where the floating menu (`.combined-floating-menu`) is supposed to be hidden by the `lg:hidden` Tailwind class.

Possible contributing factors:
1.  **Timing Issue**: The `lg:hidden` class might not be applied or rendered immediately upon breakpoint transition, causing a brief flicker or misplacement before the element is hidden.
2.  **CSS Conflict**: Other CSS rules (potentially from Tailwind's base styles or other components) might conflict with the `position: fixed` and `lg:hidden` at the breakpoint, leading to an unexpected intermediate state.
3.  **Viewport Unit Interaction**: The `height: 100vh` on `frame-container` in `index.html` combined with `position: fixed` elements and dynamic content loading could create subtle layout shifts at breakpoints, especially if the `iframe` content also has its own layout.
4.  **Iframe Interaction**: The `iframe` (`#content-frame`) might be causing unexpected layout behavior, particularly if its content has its own scrollbars or fixed elements that interact with the parent document's layout.

## Proposed Plan to Address Issues

### Phase 1: Investigation and Reproduction
1.  **Reproduce the Bug**: Attempt to consistently reproduce the "out of frame" behavior at the `lg` breakpoint by resizing the browser window or testing on devices/emulators with varying screen sizes.
2.  **Inspect Element at Breakpoint**: Use browser developer tools to inspect the `.combined-floating-menu` and its parent elements precisely at the `lg` breakpoint. Look for:
    *   Applied CSS rules, especially `display`, `position`, `bottom`, `right`.
    *   Computed styles and layout.
    *   Any `transform` or `overflow` properties on parent elements.
3.  **Test `lg:hidden` Application**: Verify if the `lg:hidden` class is being applied correctly and immediately at the breakpoint.

### Phase 2: Solution Development
1.  **CSS Adjustments**:
    *   **Ensure immediate hiding**: If it's a timing issue, consider adding a small `transition-delay` or `opacity` transition to the `lg:hidden` state to smooth out the transition, or ensure the `display: none` is applied instantly.
    *   **Breakpoint Specific Overrides**: If conflicts exist, add explicit CSS rules within a media query for the `lg` breakpoint to ensure the button is correctly hidden or positioned.
    *   **Z-index conflicts**: Check if any other elements are overlapping or affecting the button's z-index.
2.  **JavaScript Intervention (if necessary)**: If CSS alone is insufficient, consider a small JavaScript snippet to explicitly hide the button or adjust its position based on `window.innerWidth` at the breakpoint.

### Phase 3: Testing and Verification
1.  **Cross-Browser/Device Testing**: Test the fix across various browsers and devices/emulators to ensure consistent behavior.
2.  **Regression Testing**: Verify that the fix does not introduce new issues or negatively impact other responsive elements.

## Roles and Responsibilities
*   **Gemini**: Lead investigation, propose and implement CSS/JS solutions, document findings and progress.
*   **User**: Provide access to the development environment, assist in reproduction, and provide feedback on the fix.

## 2025-08-15 Update — Attempts, Outcomes, Decisions

본 섹션은 재시도 방지를 위한 실패 기록과 결정 사항을 남깁니다.

- 시도 1: CSS로 lg 이상에서 강제 숨김
  - 변경: `@media (min-width:1024px){ .combined-floating-menu{ display:none!important } }`
  - 의도: Tailwind `lg:hidden` 전환 타이밍에 발생하는 깜빡임/튀는 현상 차단
  - 결과: 개선 없음. 문제는 1→2열 카드 전환 구간(메인 그리드 브레이크)에 집중적으로 발생하며, 단순 숨김은 근본 원인(레이아웃 전환/푸터 스택 상호작용)을 해소하지 못함
  - 결정: 동일 접근 재시도 금지

- 시도 2: 고정 메뉴를 body로 이동 + 최상위 z-index
  - 변경: 런타임에서 `.combined-floating-menu`를 `document.body`로 이동, `z-index` 대폭 상향, `safe-area-inset-bottom` 보정
  - 의도: 상위 컨테이너의 스태킹 컨텍스트/오버플로우 간섭 제거
  - 결과: 개선 없음. 메인 카드 1열→2열 전환 지점에서 버튼이 푸터 아래로 가려지거나 프레임 밖으로 벗어나는 현상 지속
  - 결정: 동일 접근 재시도 금지

- 조치: 위 두 변경은 원본 파일에서 모두 원복 완료. 향후 원본 파일 직접 수정 없이 오버레이(임시 CSS/JS)로만 재현·검증 후 확정안 문서화 → 사용자 승인 시에만 반영

- 다음 단계(검증 계획):
  - 재현 조건 정밀화: DevTools 모바일 모드, 메인(100x-main.html), 1열→2열(약 sm=640px) 전환 구간 픽셀단위 확인
  - 원인 가설 점검: 푸터의 포지셔닝/스택, 상위 요소 transform/overflow, iframe 상호작용, Tailwind 유틸 조합
  - 수정 전략: (A) 전환 구간 전용 오버레이 CSS로 위치/오프셋 확정, (B) 필요 시 resize 가드 JS로 즉시 보정
