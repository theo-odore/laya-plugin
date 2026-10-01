---
name: laya-router
description: Adaptive task-aware model routing and intelligence layer for AI coding agents.
---

# Laya Router

Laya Router classifies incoming tasks and guides model selection across coding agent runtimes (Antigravity, Claude Code, etc.):
- **`deep_build`**: Complex system development, large architectures, deep reasoning (`claude-opus-4-6-thinking` / `gemini-3.1-pro-high`).
- **`bug_fix`**: Debugging, runtime exceptions, crash resolution (`claude-sonnet-4-6` / `claude-3-7-sonnet`).
- **`simple_change`**: Cosmetic, styling, minor textual modifications (`gemini-3.8-flash-low` / `claude-3-5-haiku`).

When invoked or reporting status, summarize current route classification and confidence.
