---
name: laya-router
description: Adaptive task-aware model routing and intelligence layer for Antigravity.
---

# Laya Router

Laya Router classifies incoming tasks and guides Antigravity model selection:
- **`deep_build`**: Complex system development, large architectures, deep reasoning (`claude-opus-4-6-thinking` / `gemini-3.1-pro-high`).
- **`bug_fix`**: Debugging, runtime exceptions, crash resolution (`claude-sonnet-4-6` / `gemini-3.8-flash-high`).
- **`simple_change`**: Cosmetic, styling, minor textual modifications (`gemini-3.8-flash-low`).

When invoked or reporting status, summarize current route classification and confidence.
