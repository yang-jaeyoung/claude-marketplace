---
name: az:analyze-vue
description: Systematically analyze a Vue.js project structure, components, and dependencies to generate architecture documentation
argument-hint: "[target-path]"
allowed-tools: Read, Grep, Glob, Bash
---

# Analyze Vue Command

Perform comprehensive analysis of a Vue.js project to understand structure, components, and generate documentation.

## Instructions

Execute analysis in 4 phases as defined in the skill:

### Phase 1: Entry Point Analysis (Project Detection)

```bash
# 1. Project metadata
cat package.json | head -50

# 2. Build configuration
ls -la vite.config.* vue.config.* nuxt.config.* 2>/dev/null

# 3. App initialization
cat src/main.ts 2>/dev/null || cat src/main.js
```

**Collect:**
- Vue version (2.x / 3.x)
- Build tool (Vite / Webpack / Nuxt)
- State management (Vuex / Pinia / none)
- Router usage
- TypeScript usage
- UI framework (Vuetify / Element / Quasar)

### Phase 2: Structure Classification

```bash
# Directory structure
find src -type d -maxdepth 3 | head -50

# Vue file distribution
find src -name "*.vue" | wc -l
find src -name "*.vue" -path "*/views/*" | wc -l
find src -name "*.vue" -path "*/components/*" | wc -l

# Route structure = feature list
cat src/router/index.ts 2>/dev/null || cat src/router/index.js
```

**Identify architecture pattern:**
| Pattern | Characteristic | Strategy |
|---------|---------------|----------|
| Pages-based | `pages/` folder | Vertical by page |
| Views/Components | `views/` + `components/` | By route |
| Feature-based | `features/` or `modules/` | By domain |
| Atomic Design | `atoms/molecules/organisms/` | By layer |

### Phase 3: Module Analysis

**3.1 Component Dependencies**
```bash
# Most imported components (core components)
grep -rh "import.*from.*components" src --include="*.vue" --include="*.ts" | \
  sed "s/.*from ['\"]//;s/['\"].*//" | sort | uniq -c | sort -rn | head -20
```

**3.2 Store Structure**
```bash
# Pinia stores
find src -name "*.ts" -path "*stores*" -o -name "*.ts" -path "*store*"
```

**3.3 API Layer**
```bash
# API patterns
find src -type f \( -path "*api*" -o -path "*services*" \) -name "*.ts"
```

### Phase 4: Documentation Generation

Generate the following outputs:

1. **ARCHITECTURE.md** - Project overview with:
   - Vue version, build tool, state management
   - Directory structure
   - Core modules table
   - Component hierarchy (Mermaid)
   - Data flow diagram (Mermaid)
   - API endpoints
   - Dependencies

2. **Component Diagrams** - Mermaid format

3. **Route Map** - Page structure visualization

## Utility Scripts

Located at `${CLAUDE_PLUGIN_ROOT}/skills/vue-project-analyzer/scripts/`:

| Script | Purpose |
|--------|---------|
| `find_unused.sh` | Find unused components |
| `check_circular.sh` | Detect circular dependencies |
| `generate_architecture.py` | Generate architecture doc |
| `generate_diagrams.py` | Generate Mermaid diagrams |

## Usage Examples

```
/az:analyze-vue
```

## Reference Materials

- Detailed patterns: `${CLAUDE_PLUGIN_ROOT}/skills/vue-project-analyzer/references/analysis-patterns.md`
- Vue 2→3 migration: `${CLAUDE_PLUGIN_ROOT}/skills/vue-project-analyzer/references/migration-checklist.md`

## Error Handling

| Situation | Alternative |
|-----------|-------------|
| No `src/` | Check `app/`, `lib/`, `client/` |
| No Vue files | Verify Vue project via package.json |
| No router | Check Nuxt file-based routing or `pages/` |
| No TypeScript | Search `.js` extensions instead |
| No store | Check Composition API `provide/inject` or composables |
