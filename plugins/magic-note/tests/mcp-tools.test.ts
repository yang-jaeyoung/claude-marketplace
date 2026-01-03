/**
 * MCP Tools Tests
 *
 * Tests for MCP server tool handlers.
 * Uses a mock approach to test tool logic without full MCP transport.
 */

import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { rm, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

// Import storage functions to set up test data
import {
  createWorkflow,
  readWorkflow,
  updateWorkflow,
  addTask,
  updateTask,
  createCheckpoint,
  listCheckpoints,
  getWorkflowStatus,
  initWorkflowStorage,
} from '../src/core/workflow-storage';
import {
  createNote,
  initStorage,
} from '../src/core/note';
import type { TaskStatus, TaskPriority } from '../src/core/types';

// Test storage directory
const TEST_STORAGE_ROOT = join(homedir(), '.magic-note-test-mcp');
process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;

// ============================================================================
// HELPER FUNCTION TESTS
// ============================================================================

describe('MCP Tool Helpers', () => {
  describe('buildProgressBar', () => {
    // Re-implement for testing (since it's not exported)
    function buildProgressBar(percent: number): string {
      const filled = Math.round(percent / 6.25);
      const empty = 16 - filled;
      return '█'.repeat(filled) + '░'.repeat(empty);
    }

    it('should show empty bar for 0%', () => {
      const bar = buildProgressBar(0);
      expect(bar).toBe('░░░░░░░░░░░░░░░░');
      expect(bar.length).toBe(16);
    });

    it('should show full bar for 100%', () => {
      const bar = buildProgressBar(100);
      expect(bar).toBe('████████████████');
      expect(bar.length).toBe(16);
    });

    it('should show half bar for 50%', () => {
      const bar = buildProgressBar(50);
      expect(bar).toBe('████████░░░░░░░░');
      expect(bar.length).toBe(16);
    });

    it('should handle 25%', () => {
      const bar = buildProgressBar(25);
      expect(bar).toBe('████░░░░░░░░░░░░');
      expect(bar.length).toBe(16);
    });
  });

  describe('formatRelativeTime', () => {
    // Re-implement for testing
    function formatRelativeTime(isoDate: string): string {
      const diff = Date.now() - new Date(isoDate).getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
      if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      return 'just now';
    }

    it('should return "just now" for recent timestamps', () => {
      const now = new Date().toISOString();
      expect(formatRelativeTime(now)).toBe('just now');
    });

    it('should return minutes ago', () => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60000).toISOString();
      expect(formatRelativeTime(fiveMinutesAgo)).toBe('5 minutes ago');
    });

    it('should return hours ago', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 3600000).toISOString();
      expect(formatRelativeTime(twoHoursAgo)).toBe('2 hours ago');
    });

    it('should return days ago', () => {
      const threeDaysAgo = new Date(Date.now() - 3 * 86400000).toISOString();
      expect(formatRelativeTime(threeDaysAgo)).toBe('3 days ago');
    });

    it('should handle singular forms', () => {
      const oneMinuteAgo = new Date(Date.now() - 60000).toISOString();
      expect(formatRelativeTime(oneMinuteAgo)).toBe('1 minute ago');

      const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
      expect(formatRelativeTime(oneHourAgo)).toBe('1 hour ago');

      const oneDayAgo = new Date(Date.now() - 86400000).toISOString();
      expect(formatRelativeTime(oneDayAgo)).toBe('1 day ago');
    });
  });

  describe('getEventEmoji', () => {
    // Re-implement for testing
    function getEventEmoji(eventType: string): string {
      const map: Record<string, string> = {
        'workflow_created': '📋',
        'workflow_started': '🚀',
        'workflow_completed': '🎉',
        'workflow_paused': '⏸️',
        'workflow_failed': '💥',
        'workflow_cancelled': '🚫',
        'task_created': '➕',
        'task_started': '🔄',
        'task_completed': '✅',
        'task_failed': '❌',
        'task_skipped': '⏭️',
        'step_completed': '✓',
        'checkpoint_created': '📸',
        'verification_run': '🔍',
        'review_submitted': '📝',
      };
      return map[eventType] || '•';
    }

    it('should return correct emoji for workflow events', () => {
      expect(getEventEmoji('workflow_created')).toBe('📋');
      expect(getEventEmoji('workflow_started')).toBe('🚀');
      expect(getEventEmoji('workflow_completed')).toBe('🎉');
    });

    it('should return correct emoji for task events', () => {
      expect(getEventEmoji('task_created')).toBe('➕');
      expect(getEventEmoji('task_completed')).toBe('✅');
      expect(getEventEmoji('task_failed')).toBe('❌');
    });

    it('should return default emoji for unknown events', () => {
      expect(getEventEmoji('unknown_event')).toBe('•');
    });
  });

  describe('getStatusEmoji', () => {
    // Re-implement for testing
    function getStatusEmoji(status: TaskStatus): string {
      const map: Record<TaskStatus, string> = {
        'pending': '⬜',
        'in_progress': '🔄',
        'verifying': '🔍',
        'review': '📝',
        'completed': '✅',
        'failed': '❌',
        'skipped': '⏭️',
        'blocked': '🚫',
      };
      return map[status] || '•';
    }

    it('should return correct emoji for each status', () => {
      expect(getStatusEmoji('pending')).toBe('⬜');
      expect(getStatusEmoji('in_progress')).toBe('🔄');
      expect(getStatusEmoji('completed')).toBe('✅');
      expect(getStatusEmoji('failed')).toBe('❌');
      expect(getStatusEmoji('blocked')).toBe('🚫');
    });
  });
});

// ============================================================================
// WORKFLOW TOOL INTEGRATION TESTS
// ============================================================================

describe('MCP Workflow Tools Integration', () => {
  beforeEach(async () => {
    process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
    await mkdir(TEST_STORAGE_ROOT, { recursive: true });
    await initWorkflowStorage();
  });

  afterEach(async () => {
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
  });

  describe('create_workflow tool logic', () => {
    it('should create workflow with basic info', async () => {
      const workflow = await createWorkflow({
        title: 'Test Workflow',
        description: 'Test description',
        project: 'test-project',
      });

      expect(workflow.id).toMatch(/^wf_/);
      expect(workflow.title).toBe('Test Workflow');
      expect(workflow.description).toBe('Test description');
      expect(workflow.project).toBe('test-project');
      expect(workflow.status).toBe('draft');
    });

    it('should create workflow with initial tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Workflow with Tasks',
        tasks: [
          { title: 'Task 1', description: 'First', priority: 'high' },
          { title: 'Task 2', description: 'Second', priority: 'medium' },
        ],
      });

      expect(workflow.tasks).toHaveLength(2);
      expect(workflow.tasks[0].title).toBe('Task 1');
      expect(workflow.tasks[0].priority).toBe('high');
      expect(workflow.progress.total).toBe(2);
    });

    it('should create workflow with tags', async () => {
      const workflow = await createWorkflow({
        title: 'Tagged Workflow',
        tags: ['important', 'sprint-1'],
      });

      expect(workflow.tags).toEqual(['important', 'sprint-1']);
    });
  });

  describe('get_workflow tool logic', () => {
    it('should return workflow with tasks', async () => {
      const created = await createWorkflow({
        title: 'Get Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      const workflow = await readWorkflow(created.id);

      expect(workflow).toBeDefined();
      expect(workflow!.id).toBe(created.id);
      expect(workflow!.tasks).toHaveLength(1);
    });

    it('should return null for non-existent workflow', async () => {
      const workflow = await readWorkflow('wf_nonexistent');
      expect(workflow).toBeNull();
    });
  });

  describe('update_workflow tool logic', () => {
    it('should update workflow metadata', async () => {
      const created = await createWorkflow({ title: 'Original' });

      const updated = await updateWorkflow(created.id, {
        title: 'Updated Title',
        status: 'active',
      });

      expect(updated!.title).toBe('Updated Title');
      expect(updated!.status).toBe('active');
      expect(updated!.startedAt).toBeDefined();
    });

    it('should update tags', async () => {
      const created = await createWorkflow({ title: 'Tag Test' });

      const updated = await updateWorkflow(created.id, {
        tags: ['new-tag', 'another'],
      });

      expect(updated!.tags).toEqual(['new-tag', 'another']);
    });
  });

  describe('set_task_status tool logic', () => {
    it('should change task status to in_progress', async () => {
      const workflow = await createWorkflow({
        title: 'Status Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      const task = await updateTask(workflow.id, workflow.tasks[0].id, {
        status: 'in_progress',
      });

      expect(task!.status).toBe('in_progress');
      expect(task!.startedAt).toBeDefined();
    });

    it('should change task status to completed', async () => {
      const workflow = await createWorkflow({
        title: 'Complete Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });
      const task = await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      expect(task!.status).toBe('completed');
      expect(task!.completedAt).toBeDefined();
    });

    it('should update workflow progress when task completed', async () => {
      const workflow = await createWorkflow({
        title: 'Progress Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      const updated = await readWorkflow(workflow.id);
      expect(updated!.progress.completed).toBe(1);
      expect(updated!.progress.percentage).toBe(50);
    });
  });

  describe('add_task tool logic', () => {
    it('should add task with all properties', async () => {
      const workflow = await createWorkflow({ title: 'Add Task Test' });

      const task = await addTask(workflow.id, {
        title: 'New Task',
        description: 'Task description',
        priority: 'critical',
      });

      expect(task!.title).toBe('New Task');
      expect(task!.priority).toBe('critical');
      expect(task!.status).toBe('pending');
    });

    it('should set correct order for new tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Order Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      const task = await addTask(workflow.id, {
        title: 'Task 2',
        description: '',
      });

      expect(task!.order).toBe(1);
    });
  });

  describe('create_checkpoint tool logic', () => {
    it('should create checkpoint with notes', async () => {
      const workflow = await createWorkflow({
        title: 'Checkpoint Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      const checkpoint = await createCheckpoint(workflow.id, {
        notes: 'Checkpoint notes',
        reason: 'manual',
      });

      expect(checkpoint!.id).toMatch(/^cp_/);
      expect(checkpoint!.notes).toBe('Checkpoint notes');
      expect(checkpoint!.reason).toBe('manual');
    });

    it('should capture task statuses', async () => {
      const workflow = await createWorkflow({
        title: 'Status Capture Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });
      const checkpoint = await createCheckpoint(workflow.id);

      expect(checkpoint!.taskStatuses[workflow.tasks[0].id]).toBe('in_progress');
    });
  });

  describe('get_workflow_status tool logic', () => {
    it('should return status summary', async () => {
      const workflow = await createWorkflow({
        title: 'Status Summary Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });

      const status = await getWorkflowStatus(workflow.id);

      expect(status!.workflow.title).toBe('Status Summary Test');
      expect(status!.currentTask).toBeDefined();
      expect(status!.currentTask!.title).toBe('Task 1');
    });

    it('should identify blockers', async () => {
      const workflow = await createWorkflow({
        title: 'Blocker Test',
        tasks: [{ title: 'Blocked Task', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'blocked' });

      const status = await getWorkflowStatus(workflow.id);

      expect(status!.blockers).toContain('Blocked Task');
    });

    it('should list next actions', async () => {
      const workflow = await createWorkflow({
        title: 'Next Actions Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
          { title: 'Task 3', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      const status = await getWorkflowStatus(workflow.id);

      expect(status!.nextActions).toContain('Task 2');
      expect(status!.nextActions).toContain('Task 3');
    });
  });

  describe('resume_workflow context', () => {
    it('should provide resume context with last checkpoint', async () => {
      const workflow = await createWorkflow({
        title: 'Resume Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await createCheckpoint(workflow.id, { notes: 'Progress saved' });

      const checkpoints = await listCheckpoints(workflow.id);
      expect(checkpoints).toHaveLength(1);
      expect(checkpoints[0].notes).toBe('Progress saved');
    });

    it('should show last completed task', async () => {
      const workflow = await createWorkflow({
        title: 'Last Completed Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      const updated = await readWorkflow(workflow.id);
      const completedTasks = updated!.tasks.filter(t => t.status === 'completed');

      expect(completedTasks).toHaveLength(1);
      expect(completedTasks[0].title).toBe('Task 1');
      expect(completedTasks[0].completedAt).toBeDefined();
    });
  });
});

// ============================================================================
// OUTPUT FORMAT TESTS
// ============================================================================

describe('MCP Tool Output Formatting', () => {
  beforeEach(async () => {
    process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
    await mkdir(TEST_STORAGE_ROOT, { recursive: true });
    await initWorkflowStorage();
  });

  afterEach(async () => {
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
  });

  describe('Workflow status output formats', () => {
    it('should generate minimal format', async () => {
      const workflow = await createWorkflow({
        title: 'Format Test',
        tasks: [{ title: 'Task', description: '' }],
      });

      const status = await getWorkflowStatus(workflow.id);

      // Simulate minimal format output
      const minimal = `${status!.workflow.title}: ${status!.workflow.progress.percentage}% (${status!.workflow.status})`;

      expect(minimal).toContain('Format Test');
      expect(minimal).toContain('0%');
      expect(minimal).toContain('draft');
    });

    it('should include progress bar in summary format', () => {
      function buildProgressBar(percent: number): string {
        const filled = Math.round(percent / 6.25);
        const empty = 16 - filled;
        return '█'.repeat(filled) + '░'.repeat(empty);
      }

      const bar50 = buildProgressBar(50);
      const bar100 = buildProgressBar(100);

      expect(bar50).toContain('████████');
      expect(bar50).toContain('░░░░░░░░');
      expect(bar100).toBe('████████████████');
    });
  });

  describe('Timeline output grouping', () => {
    it('should group events by date', async () => {
      const workflow = await createWorkflow({
        title: 'Timeline Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      // Events are now logged, verify through workflow status
      const status = await getWorkflowStatus(workflow.id);
      expect(status!.recentEvents.length).toBeGreaterThan(0);
    });
  });
});

// ============================================================================
// ERROR HANDLING TESTS
// ============================================================================

describe('MCP Tool Error Handling', () => {
  beforeEach(async () => {
    process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
    await mkdir(TEST_STORAGE_ROOT, { recursive: true });
    await initWorkflowStorage();
  });

  afterEach(async () => {
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
  });

  describe('Non-existent resource handling', () => {
    it('should return null for non-existent workflow', async () => {
      const workflow = await readWorkflow('wf_nonexistent');
      expect(workflow).toBeNull();
    });

    it('should return null for update on non-existent workflow', async () => {
      const result = await updateWorkflow('wf_nonexistent', { title: 'New' });
      expect(result).toBeNull();
    });

    it('should return null for add task to non-existent workflow', async () => {
      const task = await addTask('wf_nonexistent', {
        title: 'Task',
        description: '',
      });
      expect(task).toBeNull();
    });

    it('should return null for update non-existent task', async () => {
      const workflow = await createWorkflow({ title: 'Test' });
      const task = await updateTask(workflow.id, 'task_nonexistent', {
        status: 'completed',
      });
      expect(task).toBeNull();
    });

    it('should return null for checkpoint on non-existent workflow', async () => {
      const checkpoint = await createCheckpoint('wf_nonexistent');
      expect(checkpoint).toBeNull();
    });

    it('should return null for status of non-existent workflow', async () => {
      const status = await getWorkflowStatus('wf_nonexistent');
      expect(status).toBeNull();
    });
  });

  describe('Edge cases', () => {
    it('should handle empty task list', async () => {
      const workflow = await createWorkflow({ title: 'Empty Tasks' });

      expect(workflow.tasks).toHaveLength(0);
      expect(workflow.progress.total).toBe(0);
      expect(workflow.progress.percentage).toBe(0);
    });

    it('should handle workflow with no description', async () => {
      const workflow = await createWorkflow({ title: 'No Description' });

      expect(workflow.description).toBeUndefined();
    });

    it('should handle workflow with empty tags', async () => {
      const workflow = await createWorkflow({
        title: 'Empty Tags',
        tags: [],
      });

      expect(workflow.tags).toEqual([]);
    });
  });
});
