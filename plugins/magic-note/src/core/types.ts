/**
 * Core type definitions for Magic Note
 *
 * Evolution: Note Storage → Workflow Management
 * Patterns integrated from competitive analysis:
 * - Confidence Checker (SuperClaude_Framework)
 * - Bite-Sized Tasks (superpowers)
 * - Memory Schema (SuperClaude_Plugin)
 * - Reflexion Pattern (SuperClaude_Framework)
 * - Verification Gate (superpowers)
 * - Two-Stage Review (superpowers)
 * - Batch Execution (superpowers)
 */

// ============================================================================
// CORE NOTE TYPES (Backward Compatible)
// ============================================================================

// Note types - 'mistake' added for Reflexion Pattern
export type NoteType = 'prompt' | 'plan' | 'choice' | 'insight' | 'mistake';

// Supported content formats
export type ContentFormat = 'markdown' | 'text' | 'xml' | 'yaml';

// Note metadata (frontmatter)
export interface NoteMeta {
  id: string;
  type: NoteType;
  title: string;
  tags: string[];
  project: string;
  format: ContentFormat;
  created: string; // ISO 8601
  updated: string; // ISO 8601
}

// Full note with content
export interface Note extends NoteMeta {
  content: string;
}

// Note creation input
export interface CreateNoteInput {
  type: NoteType;
  title: string;
  content: string;
  tags?: string[];
  project?: string;
  format?: ContentFormat;
}

// Note update input
export interface UpdateNoteInput {
  title?: string;
  content?: string;
  type?: NoteType;
  tags?: string[];
  project?: string;
  format?: ContentFormat;
}

// Note filter options
export interface NoteFilter {
  type?: NoteType;
  tags?: string[];
  project?: string;
  search?: string;
}

// Template definition
export interface Template {
  name: string;
  type: NoteType;
  tags: string[];
  content: string;
  description?: string;
  created: string;
}

// Template creation input
export interface CreateTemplateInput {
  name: string;
  type: NoteType;
  content: string;
  tags?: string[];
  description?: string;
}

// Project definition
export interface Project {
  name: string;
  description?: string;
  created: string;
  noteCount: number;
}

// App configuration
export interface AppConfig {
  version: string;
  defaultProject: string;
  defaultEditor: string;
  defaultFormat: ContentFormat;
  dateFormat: string;
}

// Index entry for fast lookup
export interface IndexEntry {
  id: string;
  type: NoteType;
  title: string;
  tags: string[];
  project: string;
  created: string;
  updated: string;
}

// Full index structure
export interface NoteIndex {
  version: string;
  lastUpdated: string;
  entries: IndexEntry[];
}

// Export format options
export type ExportFormat = 'json' | 'markdown' | 'yaml';

// Export options
export interface ExportOptions {
  format: ExportFormat;
  project?: string;
  tags?: string[];
  type?: NoteType;
  outputPath?: string;
}

// Import result
export interface ImportResult {
  success: number;
  failed: number;
  errors: string[];
}

// CLI command result
export interface CommandResult<T = void> {
  success: boolean;
  data?: T;
  error?: string;
}

// Storage paths
export interface StoragePaths {
  root: string;        // ~/.magic-note
  projects: string;    // ~/.magic-note/projects
  templates: string;   // ~/.magic-note/templates
  config: string;      // ~/.magic-note/config.yaml
  index: string;       // ~/.magic-note/index.json
  workflows: string;   // ~/.magic-note/workflows
  workspaces: string;  // ~/.magic-note/workspaces
}

// ============================================================================
// WORKFLOW TYPES (New - Workflow Management Evolution)
// ============================================================================

// Workflow status lifecycle
export type WorkflowStatus =
  | 'draft'       // Initial planning
  | 'ready'       // All tasks defined, ready to execute
  | 'active'      // Currently executing
  | 'paused'      // Temporarily suspended
  | 'blocked'     // Waiting for external dependency
  | 'completed'   // Successfully finished
  | 'failed'      // Terminated with errors
  | 'cancelled';  // Manually cancelled

// Task status with Verification Gate support
export type TaskStatus =
  | 'pending'       // Not started
  | 'in_progress'   // Currently working
  | 'verifying'     // Running verification (Verification Gate)
  | 'review'        // Awaiting review (Two-Stage Review)
  | 'completed'     // Done and verified
  | 'failed'        // Failed verification or execution
  | 'skipped'       // Intentionally skipped
  | 'blocked';      // Waiting for dependency

// Task priority levels
export type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

// ============================================================================
// CONFIDENCE CHECKER PATTERN (from SuperClaude_Framework)
// ============================================================================

/**
 * Confidence dimension for pre-implementation validation
 * Score: 0.0 (no confidence) to 1.0 (full confidence)
 */
export interface ConfidenceDimension {
  dimension: string;      // e.g., 'understanding', 'approach', 'risks'
  score: number;          // 0.0 - 1.0
  evidence: string;       // Why this score
  blockers?: string[];    // What prevents higher score
}

/**
 * Confidence check result before task execution
 */
export interface TaskConfidence {
  overall: number;                    // Weighted average (0.0 - 1.0)
  dimensions: ConfidenceDimension[];
  threshold: number;                  // Minimum required (default: 0.7)
  passed: boolean;                    // overall >= threshold
  checkedAt: string;                  // ISO 8601
  recommendation?: 'proceed' | 'clarify' | 'research' | 'defer';
}

// ============================================================================
// BITE-SIZED TASKS PATTERN (from superpowers)
// ============================================================================

/**
 * Atomic task step (2-5 minute granularity)
 */
export interface TaskStep {
  id: string;
  description: string;
  estimatedMinutes: number;           // 2-5 minutes ideal
  verificationCommand?: string;       // Command to verify completion
  completed: boolean;
  completedAt?: string;               // ISO 8601
  evidence?: string;                  // Proof of completion
}

// ============================================================================
// VERIFICATION GATE PATTERN (from superpowers)
// ============================================================================

/**
 * Verification gate - "evidence before claims"
 */
export interface VerificationGate {
  command: string;                    // What to run
  expectedOutput?: string;            // What success looks like
  exitCode?: number;                  // Expected exit code (default: 0)
  timeout?: number;                   // Timeout in seconds
}

/**
 * Task completion gate with verification requirements
 */
export interface TaskCompletionGate {
  verificationRequired: boolean;
  verifications: VerificationGate[];
  lastVerifiedAt?: string;            // ISO 8601
  lastVerificationResult?: {
    passed: boolean;
    output: string;
    exitCode: number;
    duration: number;                 // milliseconds
  };
}

// ============================================================================
// TWO-STAGE REVIEW PATTERN (from superpowers)
// ============================================================================

export type ReviewType = 'spec_compliance' | 'code_quality';
export type ReviewResult = 'approved' | 'needs_changes' | 'rejected';

/**
 * Review record for two-stage review process
 */
export interface TaskReview {
  type: ReviewType;
  result: ReviewResult;
  reviewer?: string;                  // Agent or human identifier
  feedback?: string;
  issues?: string[];
  reviewedAt: string;                 // ISO 8601
  iteration: number;                  // Review round (1, 2, 3...)
}

// ============================================================================
// CORE TASK DEFINITION
// ============================================================================

/**
 * Task within a workflow
 * Integrates: Confidence, Bite-Sized, Verification, Review patterns
 */
export interface Task {
  id: string;
  workflowId: string;

  // Basic info
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;

  // Ordering and dependencies
  order: number;
  dependsOn?: string[];               // Task IDs this depends on

  // Confidence Checker Pattern
  confidence?: TaskConfidence;

  // Bite-Sized Tasks Pattern
  steps?: TaskStep[];
  estimatedMinutes?: number;          // Total estimated time
  actualMinutes?: number;             // Actual time spent

  // Verification Gate Pattern
  completionGate?: TaskCompletionGate;

  // Two-Stage Review Pattern
  reviews?: TaskReview[];
  reviewRequired?: boolean;

  // Artifact references
  noteIds?: string[];                 // Related notes
  files?: string[];                   // Related file paths

  // Timing
  startedAt?: string;
  completedAt?: string;

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;
}

// ============================================================================
// MEMORY SCHEMA PATTERN (from SuperClaude_Plugin)
// ============================================================================

/**
 * Memory key-value for session persistence
 */
export interface MemoryEntry {
  key: string;                        // e.g., 'plan_auth', 'phase_1', 'task_1.1'
  value: string;
  category: 'plan' | 'phase' | 'task' | 'todo' | 'checkpoint' | 'decision' | 'blocker';
  createdAt: string;
  updatedAt: string;
}

/**
 * Checkpoint for session continuity
 * Enhanced with Memory Schema pattern
 */
export interface Checkpoint {
  id: string;
  workflowId: string;

  // State snapshot
  currentTaskId?: string;
  taskStatuses: Record<string, TaskStatus>;
  completedSteps: string[];           // Step IDs completed

  // Memory Schema integration
  memoryEntries: MemoryEntry[];
  sessionContext?: {
    goal: string;
    currentPhase: string;
    blockers: string[];
    decisions: string[];
    nextActions: string[];
  };

  // Context preservation
  notes?: string;                     // Human-readable summary
  pendingActions?: string[];

  // Timing
  createdAt: string;
  reason?: 'manual' | 'auto' | 'session_end' | 'phase_complete';
}

// ============================================================================
// BATCH EXECUTION PATTERN (from superpowers)
// ============================================================================

/**
 * Batch execution configuration
 */
export interface BatchExecutionConfig {
  batchSize: number;                  // Tasks per batch (default: 3)
  checkpointAfterBatch: boolean;      // Auto-checkpoint after each batch
  parallelExecution: boolean;         // Can tasks run in parallel
  stopOnFailure: boolean;             // Stop batch on first failure
}

/**
 * Batch execution state
 */
export interface BatchExecution {
  batchNumber: number;
  taskIds: string[];
  startedAt: string;
  completedAt?: string;
  status: 'running' | 'completed' | 'failed' | 'partial';
  results: Record<string, TaskStatus>;
}

// ============================================================================
// CORE WORKFLOW DEFINITION
// ============================================================================

/**
 * Workflow - Aggregate root for task management
 */
export interface Workflow {
  id: string;

  // Basic info
  title: string;
  description?: string;
  status: WorkflowStatus;

  // Hierarchy
  project: string;
  parentWorkflowId?: string;          // For sub-workflows

  // Tasks
  tasks: Task[];

  // Execution configuration
  executionConfig?: BatchExecutionConfig;
  currentBatch?: BatchExecution;

  // Checkpoints
  checkpoints: Checkpoint[];
  autoCheckpointInterval?: number;    // Minutes between auto-checkpoints

  // Note references
  planNoteId?: string;                // Source plan note
  relatedNoteIds?: string[];

  // Progress tracking
  progress: {
    total: number;
    completed: number;
    failed: number;
    percentage: number;
  };

  // Timing
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
  estimatedCompletion?: string;

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;
}

// ============================================================================
// REFLEXION PATTERN (from SuperClaude_Framework)
// ============================================================================

/**
 * Error signature for pattern matching
 */
export interface ErrorSignature {
  errorType: string;
  errorMessage: string;
  context?: string;                   // Task/test name
}

/**
 * Learned solution from past mistakes
 */
export interface LearnedSolution {
  signature: ErrorSignature;
  rootCause: string;
  solution: string;
  prevention?: string;
  learnedAt: string;
  reusedCount: number;
}

/**
 * Mistake note - extends Note for Reflexion pattern
 * Note: Use type: 'mistake' in Note
 */
export interface MistakeNoteContent {
  errorSignature: ErrorSignature;
  whatHappened: string;
  rootCause: string;
  whyMissed?: string;
  fixApplied: string;
  preventionChecklist?: string[];
  lessonLearned: string;
  taskId?: string;
  workflowId?: string;
}

// ============================================================================
// WORKFLOW EVENT SOURCING
// ============================================================================

export type WorkflowEventType =
  | 'workflow_created'
  | 'workflow_started'
  | 'workflow_paused'
  | 'workflow_resumed'
  | 'workflow_completed'
  | 'workflow_failed'
  | 'workflow_cancelled'
  | 'task_created'
  | 'task_started'
  | 'task_completed'
  | 'task_failed'
  | 'task_skipped'
  | 'step_completed'
  | 'confidence_checked'
  | 'verification_run'
  | 'review_submitted'
  | 'checkpoint_created'
  | 'memory_updated'
  | 'note_linked'
  | 'note_unlinked';

/**
 * Immutable event for history tracking
 */
export interface WorkflowEvent {
  id: string;
  workflowId: string;
  taskId?: string;
  stepId?: string;

  type: WorkflowEventType;
  payload: Record<string, unknown>;

  timestamp: string;                  // ISO 8601
  actor?: string;                     // Who/what triggered the event
}

// ============================================================================
// WORKFLOW CREATION/UPDATE INPUTS
// ============================================================================

export interface CreateWorkflowInput {
  title: string;
  description?: string;
  project?: string;
  planNoteId?: string;
  tasks?: Omit<Task, 'id' | 'workflowId'>[];
  executionConfig?: BatchExecutionConfig;
  tags?: string[];
}

export interface UpdateWorkflowInput {
  title?: string;
  description?: string;
  status?: WorkflowStatus;
  tags?: string[];
  executionConfig?: BatchExecutionConfig;
}

export interface CreateTaskInput {
  title: string;
  description: string;
  priority?: TaskPriority;
  order?: number;
  dependsOn?: string[];
  steps?: Omit<TaskStep, 'id' | 'completed'>[];
  estimatedMinutes?: number;
  reviewRequired?: boolean;
  completionGate?: TaskCompletionGate;
  noteIds?: string[];
  files?: string[];
  tags?: string[];
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  order?: number;
  dependsOn?: string[];
  tags?: string[];
}

// ============================================================================
// WORKFLOW FILTERS AND QUERIES
// ============================================================================

export interface WorkflowFilter {
  status?: WorkflowStatus | WorkflowStatus[];
  project?: string;
  tags?: string[];
  search?: string;
  hasIncomplete?: boolean;
  createdAfter?: string;
  createdBefore?: string;
}

export interface TaskFilter {
  status?: TaskStatus | TaskStatus[];
  priority?: TaskPriority | TaskPriority[];
  hasBlockers?: boolean;
  needsReview?: boolean;
  search?: string;
}

// ============================================================================
// WORKFLOW STATUS SUMMARY
// ============================================================================

export interface WorkflowStatusSummary {
  workflow: {
    id: string;
    title: string;
    status: WorkflowStatus;
    progress: Workflow['progress'];
  };
  currentTask?: {
    id: string;
    title: string;
    status: TaskStatus;
    currentStep?: TaskStep;
  };
  recentEvents: WorkflowEvent[];
  lastCheckpoint?: Checkpoint;
  blockers: string[];
  nextActions: string[];
}
