# Changelog

All notable changes to the Magic Note plugin will be documented in this file.

## [1.1.0] - 2026-01-04

### Changed

#### Breaking Change
- **Project-Local Storage**: Changed storage location from global `~/.magic-note` to project-local `.magic-note`
  - Each project now has its own isolated storage directory
  - Enables version control of notes/workflows (add to git or .gitignore)
  - Project context travels with the codebase
  - Environment variable `MAGIC_NOTE_STORAGE` still available for overrides

### Migration
If you have existing data in `~/.magic-note`, you can migrate it to your project:
```bash
cp -r ~/.magic-note /path/to/your/project/.magic-note
```

## [1.0.1] - 2026-01-03

### Fixed

#### Critical Fixes
- **Artifact Linking (#11)**: Fixed `link_artifact` and `unlink_artifact` not persisting `noteIds` on tasks and `relatedNoteIds` on workflows
  - Added `noteIds` to `UpdateTaskInput` interface
  - Added `relatedNoteIds` to `UpdateWorkflowInput` interface
  - Updated `updateTask()` and `updateWorkflow()` to handle new fields
  - Fixed `get_workflow` response to include `relatedNoteIds`

- **Bun Append Race Condition (#1)**: Fixed potential data corruption in event logs when multiple processes append concurrently
  - Changed `appendText()` to use Node.js `appendFile` for both runtimes
  - Previous Bun implementation (read + write) was not atomic

- **Unsafe Type Casting (#4)**: Added runtime type validation guards for enum types
  - Added `isWorkflowStatus()`, `isTaskStatus()`, `isTaskPriority()` type guards
  - Created safe conversion functions with validation
  - Updated MCP server to use type guards instead of raw type assertions

#### Important Fixes
- **Event Log Error Handling (#5)**: Added error metadata for corrupted event log entries
  - Created `ReadEventsResult` interface with parse error details
  - Added `readEventsWithMetadata()` function for detailed error information
  - Original `readEvents()` preserved for backward compatibility

- **Dependency Resolution Performance (#6)**: Optimized from O(n²) to O(n) complexity
  - `getNextBatch()` now uses `Map<taskId, Task>` for O(1) lookups
  - Significant performance improvement for large workflows (50+ tasks)

- **Task Reorder Efficiency (#10)**: Added batch reorder operation
  - New `reorderTasks()` function performs single file write
  - Previously called `updateTask()` N times (N file writes)
  - `reorder_tasks` MCP tool now uses batch function

- **Step Completion Index (#3)**: Fixed index not updating after step completion
  - `completeStep()` now updates workflow index for accurate `updatedAt`

### Added
- Type guard functions: `isWorkflowStatus()`, `isTaskStatus()`, `isTaskPriority()`
- Safe type assertion functions: `assertWorkflowStatus()`, `assertTaskStatus()`, `assertTaskPriority()`
- `ReadEventsResult` interface for detailed event parsing results
- `readEventsWithMetadata()` function for error-aware event reading
- `reorderTasks()` batch function for efficient task reordering
- `artifact-linking.test.ts` - Integration tests for artifact linking

### Changed
- `appendText()` now uses atomic `appendFile` for both Bun and Node.js runtimes
- `get_workflow` response now includes `relatedNoteIds` field
- `getNextBatch()` uses Map-based O(1) task lookups

## [1.0.0] - 2026-01-03

### Added
- Initial workflow management system
- 20+ MCP tools for workflow operations
- Event sourcing with JSONL append-only logs
- Checkpoint and restore functionality
- Batch execution helpers
- 4 workflow skills (workflow, resume, status, checkpoint)
- Multi-runtime support (Bun + Node.js)
