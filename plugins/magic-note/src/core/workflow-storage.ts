/**
 * Workflow Storage Layer
 *
 * Provides CRUD operations for Workflows, Tasks, Checkpoints, and Events.
 * Implements Event Sourcing pattern with JSONL append-only log.
 *
 * Storage Structure:
 *   ~/.magic-note/workflows/
 *     ├── index.json           # Workflow index for fast lookup
 *     ├── {workflowId}/
 *     │   ├── workflow.json    # Workflow state
 *     │   ├── events.jsonl     # Event log (append-only)
 *     │   └── checkpoints/
 *     │       └── {checkpointId}.json
 */

import { mkdir, readdir, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { nanoid } from 'nanoid';
import type {
  Workflow,
  Task,
  TaskStep,
  Checkpoint,
  WorkflowEvent,
  WorkflowEventType,
  WorkflowStatus,
  TaskStatus,
  TaskPriority,
  CreateWorkflowInput,
  UpdateWorkflowInput,
  CreateTaskInput,
  UpdateTaskInput,
  WorkflowFilter,
  TaskFilter,
  WorkflowStatusSummary,
  BatchExecution,
} from './types';
import {
  getStoragePaths,
  fileExists,
  readFileContent,
  writeFileContent,
  deleteFile,
} from './storage';
import { readText, writeText, appendText, dirExists } from './runtime';

// ============================================================================
// CONSTANTS & HELPERS
// ============================================================================

// Valid status values for validation
const VALID_WORKFLOW_STATUSES: WorkflowStatus[] = [
  'draft', 'ready', 'active', 'paused', 'blocked', 'completed', 'failed', 'cancelled'
];

const VALID_TASK_STATUSES: TaskStatus[] = [
  'pending', 'in_progress', 'verifying', 'review', 'completed', 'failed', 'skipped', 'blocked'
];

const VALID_TASK_PRIORITIES: TaskPriority[] = ['critical', 'high', 'medium', 'low'];

// Generate unique IDs
function generateWorkflowId(): string {
  return `wf_${nanoid(10)}`;
}

function generateTaskId(): string {
  return `task_${nanoid(8)}`;
}

function generateStepId(): string {
  return `step_${nanoid(6)}`;
}

function generateCheckpointId(): string {
  return `cp_${nanoid(8)}`;
}

function generateEventId(): string {
  return `evt_${nanoid(12)}`;
}

// Safe string validation
function safeString(value: unknown, defaultValue: string, maxLength = 1000): string {
  if (typeof value === 'string' && value.length <= maxLength) {
    return value;
  }
  return defaultValue;
}

// Safe array validation
function safeStringArray(value: unknown, maxItems = 50): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === 'string' && item.length <= 100)
    .slice(0, maxItems);
}

// Validate workflow status
function safeWorkflowStatus(value: unknown): WorkflowStatus {
  if (typeof value === 'string' && VALID_WORKFLOW_STATUSES.includes(value as WorkflowStatus)) {
    return value as WorkflowStatus;
  }
  return 'draft';
}

// Validate task status
function safeTaskStatus(value: unknown): TaskStatus {
  if (typeof value === 'string' && VALID_TASK_STATUSES.includes(value as TaskStatus)) {
    return value as TaskStatus;
  }
  return 'pending';
}

// Validate task priority
function safeTaskPriority(value: unknown): TaskPriority {
  if (typeof value === 'string' && VALID_TASK_PRIORITIES.includes(value as TaskPriority)) {
    return value as TaskPriority;
  }
  return 'medium';
}

// ============================================================================
// PATH HELPERS
// ============================================================================

function getWorkflowsRoot(): string {
  return getStoragePaths().workflows;
}

function getWorkflowIndexPath(): string {
  return join(getWorkflowsRoot(), 'index.json');
}

function getWorkflowDir(workflowId: string): string {
  return join(getWorkflowsRoot(), workflowId);
}

function getWorkflowPath(workflowId: string): string {
  return join(getWorkflowDir(workflowId), 'workflow.json');
}

function getEventsPath(workflowId: string): string {
  return join(getWorkflowDir(workflowId), 'events.jsonl');
}

function getCheckpointsDir(workflowId: string): string {
  return join(getWorkflowDir(workflowId), 'checkpoints');
}

function getCheckpointPath(workflowId: string, checkpointId: string): string {
  return join(getCheckpointsDir(workflowId), `${checkpointId}.json`);
}

// ============================================================================
// WORKFLOW INDEX
// ============================================================================

interface WorkflowIndexEntry {
  id: string;
  title: string;
  status: WorkflowStatus;
  project: string;
  progress: { total: number; completed: number; percentage: number };
  createdAt: string;
  updatedAt: string;
  tags?: string[];
}

interface WorkflowIndex {
  version: string;
  lastUpdated: string;
  entries: WorkflowIndexEntry[];
}

function createEmptyWorkflowIndex(): WorkflowIndex {
  return {
    version: '1.0',
    lastUpdated: new Date().toISOString(),
    entries: [],
  };
}

async function readWorkflowIndex(): Promise<WorkflowIndex> {
  const indexPath = getWorkflowIndexPath();

  if (!(await fileExists(indexPath))) {
    return createEmptyWorkflowIndex();
  }

  try {
    const content = await readText(indexPath);
    const parsed = JSON.parse(content);

    if (!parsed || typeof parsed !== 'object' || !Array.isArray(parsed.entries)) {
      console.error('Invalid workflow index structure, resetting');
      return createEmptyWorkflowIndex();
    }

    return parsed as WorkflowIndex;
  } catch (error) {
    console.error('Failed to parse workflow index:', error);
    return createEmptyWorkflowIndex();
  }
}

async function writeWorkflowIndex(index: WorkflowIndex): Promise<void> {
  const indexPath = getWorkflowIndexPath();
  index.lastUpdated = new Date().toISOString();
  await writeText(indexPath, JSON.stringify(index, null, 2));
}

function workflowToIndexEntry(workflow: Workflow): WorkflowIndexEntry {
  return {
    id: workflow.id,
    title: workflow.title,
    status: workflow.status,
    project: workflow.project,
    progress: {
      total: workflow.progress.total,
      completed: workflow.progress.completed,
      percentage: workflow.progress.percentage,
    },
    createdAt: workflow.createdAt,
    updatedAt: workflow.updatedAt,
    tags: workflow.tags,
  };
}

// ============================================================================
// WORKFLOW CRUD
// ============================================================================

/**
 * Create a new workflow
 */
export async function createWorkflow(input: CreateWorkflowInput): Promise<Workflow> {
  const id = generateWorkflowId();
  const now = new Date().toISOString();

  // Process tasks if provided
  const tasks: Task[] = (input.tasks || []).map((taskInput, index) => ({
    id: generateTaskId(),
    workflowId: id,
    title: taskInput.title,
    description: taskInput.description,
    priority: taskInput.priority || 'medium',
    status: 'pending' as TaskStatus,
    order: taskInput.order ?? index,
    dependsOn: taskInput.dependsOn,
    confidence: taskInput.confidence,
    steps: taskInput.steps?.map(step => ({
      ...step,
      id: generateStepId(),
      completed: false,
    })),
    estimatedMinutes: taskInput.estimatedMinutes,
    completionGate: taskInput.completionGate,
    reviewRequired: taskInput.reviewRequired,
    noteIds: taskInput.noteIds,
    files: taskInput.files,
    tags: taskInput.tags,
  }));

  const workflow: Workflow = {
    id,
    title: input.title,
    description: input.description,
    status: 'draft',
    project: input.project || 'default',
    tasks,
    executionConfig: input.executionConfig,
    checkpoints: [],
    planNoteId: input.planNoteId,
    progress: {
      total: tasks.length,
      completed: 0,
      failed: 0,
      percentage: 0,
    },
    createdAt: now,
    updatedAt: now,
    tags: input.tags,
  };

  // Ensure directories exist
  await mkdir(getWorkflowDir(id), { recursive: true });
  await mkdir(getCheckpointsDir(id), { recursive: true });

  // Write workflow file
  await writeText(getWorkflowPath(id), JSON.stringify(workflow, null, 2));

  // Create empty events file
  await writeText(getEventsPath(id), '');

  // Log creation event
  await appendEvent(id, {
    type: 'workflow_created',
    payload: { title: input.title, taskCount: tasks.length },
  });

  // Update index
  const index = await readWorkflowIndex();
  index.entries.push(workflowToIndexEntry(workflow));
  await writeWorkflowIndex(index);

  return workflow;
}

/**
 * Read a workflow by ID
 */
export async function readWorkflow(id: string): Promise<Workflow | null> {
  const workflowPath = getWorkflowPath(id);

  if (!(await fileExists(workflowPath))) {
    return null;
  }

  try {
    const content = await readText(workflowPath);
    return JSON.parse(content) as Workflow;
  } catch (error) {
    console.error(`Failed to read workflow ${id}:`, error);
    return null;
  }
}

/**
 * Update an existing workflow
 */
export async function updateWorkflow(
  id: string,
  input: UpdateWorkflowInput
): Promise<Workflow | null> {
  const workflow = await readWorkflow(id);

  if (!workflow) {
    return null;
  }

  const previousStatus = workflow.status;

  // Apply updates
  if (input.title !== undefined) workflow.title = input.title;
  if (input.description !== undefined) workflow.description = input.description;
  if (input.status !== undefined) workflow.status = input.status;
  if (input.tags !== undefined) workflow.tags = input.tags;
  if (input.executionConfig !== undefined) workflow.executionConfig = input.executionConfig;

  workflow.updatedAt = new Date().toISOString();

  // Track status changes
  if (input.status && input.status !== previousStatus) {
    // Set timing fields based on status
    if (input.status === 'active' && !workflow.startedAt) {
      workflow.startedAt = workflow.updatedAt;
    } else if (input.status === 'completed' || input.status === 'failed' || input.status === 'cancelled') {
      workflow.completedAt = workflow.updatedAt;
    }

    // Log status change event
    await appendEvent(id, {
      type: getWorkflowStatusEventType(input.status),
      payload: { previousStatus, newStatus: input.status },
    });
  }

  // Write updated workflow
  await writeText(getWorkflowPath(id), JSON.stringify(workflow, null, 2));

  // Update index
  const index = await readWorkflowIndex();
  const entryIndex = index.entries.findIndex(e => e.id === id);
  if (entryIndex >= 0) {
    index.entries[entryIndex] = workflowToIndexEntry(workflow);
    await writeWorkflowIndex(index);
  }

  return workflow;
}

/**
 * Delete a workflow and all its data
 */
export async function deleteWorkflow(id: string): Promise<boolean> {
  const workflowDir = getWorkflowDir(id);

  // Use dirExists for directory check (fileExists only works for files in Bun)
  if (!(await dirExists(workflowDir))) {
    return false;
  }

  // Remove entire workflow directory
  await rm(workflowDir, { recursive: true, force: true });

  // Update index
  const index = await readWorkflowIndex();
  index.entries = index.entries.filter(e => e.id !== id);
  await writeWorkflowIndex(index);

  return true;
}

/**
 * List workflows with optional filtering
 */
export async function listWorkflows(filter?: WorkflowFilter): Promise<WorkflowIndexEntry[]> {
  const index = await readWorkflowIndex();

  if (!filter) {
    return index.entries.sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }

  const searchLower = filter.search?.toLowerCase();
  const filterTags = filter.tags && filter.tags.length > 0 ? filter.tags : null;
  const filterStatuses = filter.status
    ? (Array.isArray(filter.status) ? filter.status : [filter.status])
    : null;

  const filtered = index.entries.filter(entry => {
    // Status filter
    if (filterStatuses && !filterStatuses.includes(entry.status)) return false;

    // Project filter
    if (filter.project && entry.project !== filter.project) return false;

    // Tags filter (any match)
    if (filterTags && entry.tags && !filterTags.some(tag => entry.tags!.includes(tag))) return false;

    // Has incomplete filter
    if (filter.hasIncomplete !== undefined) {
      const hasIncomplete = entry.progress.completed < entry.progress.total;
      if (filter.hasIncomplete !== hasIncomplete) return false;
    }

    // Date range filters
    if (filter.createdAfter && new Date(entry.createdAt) < new Date(filter.createdAfter)) return false;
    if (filter.createdBefore && new Date(entry.createdAt) > new Date(filter.createdBefore)) return false;

    // Search filter
    if (searchLower) {
      const titleMatch = entry.title.toLowerCase().includes(searchLower);
      const tagMatch = entry.tags?.some(tag => tag.toLowerCase().includes(searchLower)) || false;
      if (!titleMatch && !tagMatch) return false;
    }

    return true;
  });

  return filtered.sort((a, b) =>
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
}

// Helper to get workflow status event type
function getWorkflowStatusEventType(status: WorkflowStatus): WorkflowEventType {
  const statusEventMap: Record<WorkflowStatus, WorkflowEventType> = {
    draft: 'workflow_created',
    ready: 'workflow_created',
    active: 'workflow_started',
    paused: 'workflow_paused',
    blocked: 'workflow_paused',
    completed: 'workflow_completed',
    failed: 'workflow_failed',
    cancelled: 'workflow_cancelled',
  };
  return statusEventMap[status];
}

// ============================================================================
// TASK CRUD (within Workflow context)
// ============================================================================

/**
 * Add a task to a workflow
 */
export async function addTask(
  workflowId: string,
  input: CreateTaskInput
): Promise<Task | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const task: Task = {
    id: generateTaskId(),
    workflowId,
    title: input.title,
    description: input.description,
    priority: input.priority || 'medium',
    status: 'pending',
    order: input.order ?? workflow.tasks.length,
    dependsOn: input.dependsOn,
    steps: input.steps?.map(step => ({
      ...step,
      id: generateStepId(),
      completed: false,
    })),
    estimatedMinutes: input.estimatedMinutes,
    completionGate: input.completionGate,
    reviewRequired: input.reviewRequired,
    noteIds: input.noteIds,
    files: input.files,
    tags: input.tags,
  };

  workflow.tasks.push(task);
  workflow.progress.total = workflow.tasks.length;
  updateWorkflowProgress(workflow);
  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  await appendEvent(workflowId, {
    type: 'task_created',
    taskId: task.id,
    payload: { title: input.title, order: task.order },
  });

  // Update index
  const index = await readWorkflowIndex();
  const entryIndex = index.entries.findIndex(e => e.id === workflowId);
  if (entryIndex >= 0) {
    index.entries[entryIndex] = workflowToIndexEntry(workflow);
    await writeWorkflowIndex(index);
  }

  return task;
}

/**
 * Update a task within a workflow
 */
export async function updateTask(
  workflowId: string,
  taskId: string,
  input: UpdateTaskInput
): Promise<Task | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const taskIndex = workflow.tasks.findIndex(t => t.id === taskId);
  if (taskIndex < 0) {
    return null;
  }

  const task = workflow.tasks[taskIndex];
  const previousStatus = task.status;

  // Apply updates
  if (input.title !== undefined) task.title = input.title;
  if (input.description !== undefined) task.description = input.description;
  if (input.status !== undefined) task.status = input.status;
  if (input.priority !== undefined) task.priority = input.priority;
  if (input.order !== undefined) task.order = input.order;
  if (input.dependsOn !== undefined) task.dependsOn = input.dependsOn;
  if (input.tags !== undefined) task.tags = input.tags;

  // Track status changes
  if (input.status && input.status !== previousStatus) {
    if (input.status === 'in_progress' && !task.startedAt) {
      task.startedAt = new Date().toISOString();
    } else if (input.status === 'completed' || input.status === 'failed' || input.status === 'skipped') {
      task.completedAt = new Date().toISOString();
    }

    await appendEvent(workflowId, {
      type: getTaskStatusEventType(input.status),
      taskId,
      payload: { previousStatus, newStatus: input.status },
    });
  }

  workflow.tasks[taskIndex] = task;
  updateWorkflowProgress(workflow);
  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  // Update index
  const index = await readWorkflowIndex();
  const entryIndex = index.entries.findIndex(e => e.id === workflowId);
  if (entryIndex >= 0) {
    index.entries[entryIndex] = workflowToIndexEntry(workflow);
    await writeWorkflowIndex(index);
  }

  return task;
}

/**
 * Remove a task from a workflow
 */
export async function removeTask(workflowId: string, taskId: string): Promise<boolean> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return false;
  }

  const taskIndex = workflow.tasks.findIndex(t => t.id === taskId);
  if (taskIndex < 0) {
    return false;
  }

  workflow.tasks.splice(taskIndex, 1);

  // Re-order remaining tasks
  workflow.tasks.forEach((task, index) => {
    task.order = index;
  });

  workflow.progress.total = workflow.tasks.length;
  updateWorkflowProgress(workflow);
  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  // Update index
  const index = await readWorkflowIndex();
  const entryIndex = index.entries.findIndex(e => e.id === workflowId);
  if (entryIndex >= 0) {
    index.entries[entryIndex] = workflowToIndexEntry(workflow);
    await writeWorkflowIndex(index);
  }

  return true;
}

/**
 * Get tasks from a workflow with optional filtering
 */
export async function getTasks(
  workflowId: string,
  filter?: TaskFilter
): Promise<Task[]> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return [];
  }

  if (!filter) {
    return workflow.tasks.sort((a, b) => a.order - b.order);
  }

  const searchLower = filter.search?.toLowerCase();
  const filterStatuses = filter.status
    ? (Array.isArray(filter.status) ? filter.status : [filter.status])
    : null;
  const filterPriorities = filter.priority
    ? (Array.isArray(filter.priority) ? filter.priority : [filter.priority])
    : null;

  const filtered = workflow.tasks.filter(task => {
    if (filterStatuses && !filterStatuses.includes(task.status)) return false;
    if (filterPriorities && !filterPriorities.includes(task.priority)) return false;
    if (filter.hasBlockers !== undefined) {
      const hasBlockers = task.status === 'blocked' || (task.dependsOn && task.dependsOn.length > 0);
      if (filter.hasBlockers !== hasBlockers) return false;
    }
    if (filter.needsReview !== undefined) {
      const needsReview = task.status === 'review' || task.reviewRequired;
      if (filter.needsReview !== needsReview) return false;
    }
    if (searchLower) {
      const titleMatch = task.title.toLowerCase().includes(searchLower);
      const descMatch = task.description.toLowerCase().includes(searchLower);
      if (!titleMatch && !descMatch) return false;
    }

    return true;
  });

  return filtered.sort((a, b) => a.order - b.order);
}

// Helper to get task status event type
function getTaskStatusEventType(status: TaskStatus): WorkflowEventType {
  const statusEventMap: Record<TaskStatus, WorkflowEventType> = {
    pending: 'task_created',
    in_progress: 'task_started',
    verifying: 'verification_run',
    review: 'review_submitted',
    completed: 'task_completed',
    failed: 'task_failed',
    skipped: 'task_skipped',
    blocked: 'task_started',
  };
  return statusEventMap[status];
}

// Update workflow progress based on task statuses
function updateWorkflowProgress(workflow: Workflow): void {
  const total = workflow.tasks.length;
  const completed = workflow.tasks.filter(t => t.status === 'completed').length;
  const failed = workflow.tasks.filter(t => t.status === 'failed').length;

  workflow.progress = {
    total,
    completed,
    failed,
    percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
  };
}

// ============================================================================
// TASK STEP OPERATIONS
// ============================================================================

/**
 * Complete a step within a task
 */
export async function completeStep(
  workflowId: string,
  taskId: string,
  stepId: string,
  evidence?: string
): Promise<TaskStep | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const task = workflow.tasks.find(t => t.id === taskId);
  if (!task || !task.steps) {
    return null;
  }

  const step = task.steps.find(s => s.id === stepId);
  if (!step) {
    return null;
  }

  step.completed = true;
  step.completedAt = new Date().toISOString();
  if (evidence) {
    step.evidence = evidence;
  }

  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  await appendEvent(workflowId, {
    type: 'step_completed',
    taskId,
    stepId,
    payload: { description: step.description, evidence },
  });

  return step;
}

// ============================================================================
// EVENT SOURCING
// ============================================================================

interface EventInput {
  type: WorkflowEventType;
  taskId?: string;
  stepId?: string;
  payload: Record<string, unknown>;
  actor?: string;
}

/**
 * Append an event to the workflow event log
 */
export async function appendEvent(workflowId: string, input: EventInput): Promise<WorkflowEvent> {
  const event: WorkflowEvent = {
    id: generateEventId(),
    workflowId,
    taskId: input.taskId,
    stepId: input.stepId,
    type: input.type,
    payload: input.payload,
    timestamp: new Date().toISOString(),
    actor: input.actor,
  };

  const eventsPath = getEventsPath(workflowId);
  await appendText(eventsPath, JSON.stringify(event) + '\n');

  return event;
}

/**
 * Read all events for a workflow
 */
export async function readEvents(workflowId: string): Promise<WorkflowEvent[]> {
  const eventsPath = getEventsPath(workflowId);

  if (!(await fileExists(eventsPath))) {
    return [];
  }

  const content = await readText(eventsPath);
  const lines = content.trim().split('\n').filter(line => line.length > 0);

  const events: WorkflowEvent[] = [];
  for (const line of lines) {
    try {
      events.push(JSON.parse(line) as WorkflowEvent);
    } catch (error) {
      console.error('Failed to parse event:', error);
    }
  }

  return events;
}

/**
 * Get recent events for a workflow
 */
export async function getRecentEvents(workflowId: string, limit = 10): Promise<WorkflowEvent[]> {
  const events = await readEvents(workflowId);
  return events.slice(-limit);
}

// ============================================================================
// CHECKPOINT MANAGEMENT
// ============================================================================

/**
 * Create a checkpoint for a workflow
 */
export async function createCheckpoint(
  workflowId: string,
  options?: {
    notes?: string;
    reason?: 'manual' | 'auto' | 'session_end' | 'phase_complete';
  }
): Promise<Checkpoint | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const currentTask = workflow.tasks.find(t => t.status === 'in_progress');
  const completedSteps: string[] = [];

  // Collect all completed step IDs
  for (const task of workflow.tasks) {
    if (task.steps) {
      for (const step of task.steps) {
        if (step.completed) {
          completedSteps.push(step.id);
        }
      }
    }
  }

  const checkpoint: Checkpoint = {
    id: generateCheckpointId(),
    workflowId,
    currentTaskId: currentTask?.id,
    taskStatuses: Object.fromEntries(
      workflow.tasks.map(t => [t.id, t.status])
    ),
    completedSteps,
    memoryEntries: [],
    sessionContext: {
      goal: workflow.title,
      currentPhase: currentTask ? `Task: ${currentTask.title}` : 'Planning',
      blockers: workflow.tasks
        .filter(t => t.status === 'blocked')
        .map(t => t.title),
      decisions: [],
      nextActions: workflow.tasks
        .filter(t => t.status === 'pending')
        .slice(0, 3)
        .map(t => t.title),
    },
    notes: options?.notes,
    createdAt: new Date().toISOString(),
    reason: options?.reason || 'manual',
  };

  // Write checkpoint file
  await writeText(
    getCheckpointPath(workflowId, checkpoint.id),
    JSON.stringify(checkpoint, null, 2)
  );

  // Add to workflow
  workflow.checkpoints.push(checkpoint);
  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  await appendEvent(workflowId, {
    type: 'checkpoint_created',
    payload: {
      checkpointId: checkpoint.id,
      reason: checkpoint.reason,
      completedTasks: Object.values(checkpoint.taskStatuses).filter(s => s === 'completed').length,
    },
  });

  return checkpoint;
}

/**
 * Get a checkpoint by ID
 */
export async function getCheckpoint(
  workflowId: string,
  checkpointId: string
): Promise<Checkpoint | null> {
  const checkpointPath = getCheckpointPath(workflowId, checkpointId);

  if (!(await fileExists(checkpointPath))) {
    return null;
  }

  try {
    const content = await readText(checkpointPath);
    return JSON.parse(content) as Checkpoint;
  } catch (error) {
    console.error(`Failed to read checkpoint ${checkpointId}:`, error);
    return null;
  }
}

/**
 * List all checkpoints for a workflow
 */
export async function listCheckpoints(workflowId: string): Promise<Checkpoint[]> {
  const workflow = await readWorkflow(workflowId);
  return workflow?.checkpoints || [];
}

/**
 * Get the latest checkpoint for a workflow
 */
export async function getLatestCheckpoint(workflowId: string): Promise<Checkpoint | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow || workflow.checkpoints.length === 0) {
    return null;
  }

  // Sort by createdAt descending and return first
  const sorted = [...workflow.checkpoints].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  return sorted[0];
}

/**
 * Restore workflow state from a checkpoint
 */
export async function restoreFromCheckpoint(
  workflowId: string,
  checkpointId: string
): Promise<Workflow | null> {
  const workflow = await readWorkflow(workflowId);
  const checkpoint = await getCheckpoint(workflowId, checkpointId);

  if (!workflow || !checkpoint) {
    return null;
  }

  // Restore task statuses
  for (const task of workflow.tasks) {
    if (checkpoint.taskStatuses[task.id]) {
      task.status = checkpoint.taskStatuses[task.id];
    }

    // Restore step completion status
    if (task.steps) {
      for (const step of task.steps) {
        step.completed = checkpoint.completedSteps.includes(step.id);
        if (!step.completed) {
          step.completedAt = undefined;
          step.evidence = undefined;
        }
      }
    }
  }

  updateWorkflowProgress(workflow);
  workflow.updatedAt = new Date().toISOString();

  await writeText(getWorkflowPath(workflowId), JSON.stringify(workflow, null, 2));

  await appendEvent(workflowId, {
    type: 'checkpoint_created',
    payload: { restoredFrom: checkpointId, action: 'restore' },
  });

  return workflow;
}

// ============================================================================
// WORKFLOW STATUS SUMMARY
// ============================================================================

/**
 * Get a comprehensive status summary for a workflow
 */
export async function getWorkflowStatus(workflowId: string): Promise<WorkflowStatusSummary | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const currentTask = workflow.tasks.find(t => t.status === 'in_progress');
  const recentEvents = await getRecentEvents(workflowId, 5);
  const lastCheckpoint = await getLatestCheckpoint(workflowId);

  const blockers = workflow.tasks
    .filter(t => t.status === 'blocked')
    .map(t => t.title);

  const nextActions = workflow.tasks
    .filter(t => t.status === 'pending')
    .sort((a, b) => a.order - b.order)
    .slice(0, 3)
    .map(t => t.title);

  let currentStep: TaskStep | undefined;
  if (currentTask?.steps) {
    currentStep = currentTask.steps.find(s => !s.completed);
  }

  return {
    workflow: {
      id: workflow.id,
      title: workflow.title,
      status: workflow.status,
      progress: workflow.progress,
    },
    currentTask: currentTask ? {
      id: currentTask.id,
      title: currentTask.title,
      status: currentTask.status,
      currentStep,
    } : undefined,
    recentEvents,
    lastCheckpoint: lastCheckpoint || undefined,
    blockers,
    nextActions,
  };
}

// ============================================================================
// BATCH EXECUTION HELPERS
// ============================================================================

/**
 * Get the next batch of tasks to execute
 */
export async function getNextBatch(
  workflowId: string,
  batchSize = 3
): Promise<Task[]> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return [];
  }

  // Get pending tasks that have no blockers
  const eligibleTasks = workflow.tasks
    .filter(task => {
      if (task.status !== 'pending') return false;

      // Check if all dependencies are completed
      if (task.dependsOn && task.dependsOn.length > 0) {
        const allDepsCompleted = task.dependsOn.every(depId => {
          const dep = workflow.tasks.find(t => t.id === depId);
          return dep?.status === 'completed';
        });
        if (!allDepsCompleted) return false;
      }

      return true;
    })
    .sort((a, b) => {
      // Sort by priority first, then by order
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return a.order - b.order;
    });

  return eligibleTasks.slice(0, batchSize);
}

/**
 * Start a new batch execution
 */
export async function startBatch(workflowId: string): Promise<BatchExecution | null> {
  const workflow = await readWorkflow(workflowId);

  if (!workflow) {
    return null;
  }

  const batchSize = workflow.executionConfig?.batchSize || 3;
  const nextTasks = await getNextBatch(workflowId, batchSize);

  if (nextTasks.length === 0) {
    return null;
  }

  const batchNumber = (workflow.currentBatch?.batchNumber || 0) + 1;

  const batch: BatchExecution = {
    batchNumber,
    taskIds: nextTasks.map(t => t.id),
    startedAt: new Date().toISOString(),
    status: 'running',
    results: Object.fromEntries(nextTasks.map(t => [t.id, 'pending' as TaskStatus])),
  };

  // Mark tasks as in_progress
  for (const task of nextTasks) {
    await updateTask(workflowId, task.id, { status: 'in_progress' });
  }

  // Update workflow with current batch
  const updatedWorkflow = await readWorkflow(workflowId);
  if (updatedWorkflow) {
    updatedWorkflow.currentBatch = batch;
    updatedWorkflow.status = 'active';
    await writeText(getWorkflowPath(workflowId), JSON.stringify(updatedWorkflow, null, 2));
  }

  return batch;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize workflow storage (creates directories and empty index)
 */
export async function initWorkflowStorage(): Promise<void> {
  const workflowsRoot = getWorkflowsRoot();

  await mkdir(workflowsRoot, { recursive: true });

  const indexPath = getWorkflowIndexPath();
  if (!(await fileExists(indexPath))) {
    await writeWorkflowIndex(createEmptyWorkflowIndex());
  }
}
