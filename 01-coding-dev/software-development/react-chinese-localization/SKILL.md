---
name: react-chinese-localization
title: React/TypeScript Chinese Localization
description: Systematically localize English React/TypeScript UI components to Chinese while maintaining code functionality and build integrity
version: 1.0.0
trigger: when asked to translate, localize, or Chinese-ify a React/TypeScript project's UI
---

# React/TypeScript Chinese Localization

## Goal
Transform all user-facing English text in a React/TypeScript project to Chinese while preserving:
- Code functionality (variable names, functions, APIs unchanged)
- Build success (no TypeScript errors)
- Styling and formatting

## Prerequisites
- Node.js and npm/yarn installed
- Project has a working build system (vite, webpack, etc.)
- Source files are in `.tsx` or `.jsx` format

## Step-by-Step Process

### 1. Discover All UI Components
```bash
# Find all React components that contain UI text
find ./src -name "*.tsx" -o -name "*.jsx" | head -20

# Identify panel/page components (usually contain most UI text)
ls -la ./src/components/ | grep -i panel
ls -la ./src/pages/ 2>/dev/null || true
```

### 2. Create Translation Mapping
First read the main components to understand the UI structure. Create a glossary:

| English | Chinese | Notes |
|---------|---------|-------|
| Dashboard | 仪表盘 | Main view |
| Settings | 设置 | Configuration |
| Profile | 用户画像 / 档案 | User profile |
| What I Know | 知识概览 | Creative translation |
| What I Remember | 记忆状态 | Context-dependent |
| Active | 活跃 / 运行中 | For status |
| Silent | 静默 / 未运行 | For status |
| Load/Loading | 加载 | Actions |
| Save | 保存 | Actions |
| Cancel | 取消 | Actions |
| Delete | 删除 | Actions |

### 3. Systematic File-by-File Translation

For each component file:

1. **Read the file** to understand structure
2. **Identify translatable strings**:
   - Panel titles (`title="What I Know"`)
   - Button labels
   - Status messages
   - Descriptive text
   - Column headers
   - Navigation labels

3. **Replace English with Chinese**:
   - Only change string literals inside JSX or component props
   - Preserve: variable names, function names, CSS classes, API endpoints
   - Preserve: technical terms if they don't have good Chinese equivalents

4. **Preserve formatting**:
   - Keep indentation
   - Keep CSS-in-JS styling
   - Keep component structure

### 4. Key Translation Patterns

**Panel/Card Titles:**
```typescript
// Before
<Panel title="What I Know">

// After
<Panel title="知识概览">
```

**Status Indicators:**
```typescript
// Before
<span>{status === 'alive' ? 'Running' : 'Stopped'}</span>

// After
<span>{status === 'alive' ? '运行中' : '已停止'}</span>
```

**Labels and Descriptions:**
```typescript
// Before
<div><span>Messages:</span> {count}</div>

// After
<div><span>消息数：</span> {count}</div>
```

**Navigation:**
```typescript
// Before
{ label: 'Dashboard', value: 'dashboard' }

// After
{ label: '仪表盘', value: 'dashboard' }  // value unchanged
```

### 5. Build Verification
After all files are modified:

```bash
cd frontend  # or project root
npm run build 2>&1
```

Must see:
- ✓ No TypeScript errors
- ✓ No ESLint errors
- ✓ Build completes successfully

### 6. Deploy Updated Build

```bash
# Copy built files to deployment location
cp -r dist/* ../backend/static/
# Or wherever the production assets go
```

### 7. Verify in Browser

- Check all tabs/nav items are translated
- Check panel titles
- Check button labels
- Check status messages
- Verify no broken layouts

## Common Pitfalls

1. **Don't translate:**
   - Variable names (`const userName` → keep as is)
   - Function names (`handleClick` → keep as is)
   - CSS class names (`className="dashboard-panel"` → keep as is)
   - API endpoints (`/api/v1/sessions` → keep as is)
   - Route paths (`/dashboard` → keep as is)
   - Technical identifiers (model names like "GPT-4", "Claude")

2. **Preserve punctuation style:**
   - English: `Hello, World!`
   - Chinese: `你好，世界！` (use Chinese punctuation)

3. **Context matters:**
   - "Profile" as a noun → "用户画像"
   - "Profile" as a verb/action → "查看画像"

4. **Keep it concise:**
   - Chinese text can be wider; watch for layout breaks
   - Use shorter translations if space is tight

## Files Typically Modified

- `*Panel.tsx` - Main content panels
- `*Page.tsx` - Page components
- `TopBar.tsx` / `Header.tsx` - Navigation
- `Sidebar.tsx` - Navigation menu
- `CommandPalette.tsx` - Command interface
- `BootScreen.tsx` / `Loading.tsx` - Splash screens
- `useTheme.tsx` / `theme.ts` - Theme names

## Verification Checklist

- [ ] All navigation items translated
- [ ] All panel titles translated
- [ ] All button labels translated
- [ ] All status messages translated
- [ ] All table headers translated
- [ ] All form labels translated
- [ ] Build succeeds without errors
- [ ] No runtime errors in browser console
- [ ] Layouts not broken (text overflow, etc.)

## Example Complete Workflow

```bash
# 1. Find components
ls src/components/*.tsx

# 2. Read and translate DashboardPanel.tsx
# (replace "What I Know" with "知识概览", etc.)

# 3. Read and translate TopBar.tsx
# (replace navigation labels)

# 4. Continue for all component files...

# 5. Build
npm run build

# 6. Deploy
cp -r dist/* backend/static/

# 7. Test
curl http://localhost:3001
```
