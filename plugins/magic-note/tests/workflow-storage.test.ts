/**
 * Workflow Storage Layer Tests
 *
 * Tests for CRUD operations, Event Sourcing, and Checkpoint management.
 * Uses Bun's built-in test runner.
 */

import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { rm, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

import {
  createWorkflow,
  readWorkflow,
  updateWorkflow,
  deleteWorkflow,
  listWorkflows,
  addTask,
  updateTask,
  removeTask,
  getTasks,
  completeStep,
  createCheckpoint,
  listCheckpoints,
  getLatestCheckpoint,
  restoreFromCheckpoint,
  getWorkflowStatus,
  readEvents,
  getRecentEvents,
  getNextBatch,
  startBatch,
  initWorkflowStorage,
} from '../src/core/workflow-storage';
import type { TaskPriority, TaskStatus } from '../src/core/types';

// Test storage directory (isolated from production)
const TEST_STORAGE_ROOT = join(homedir(), '.magic-note-test');

// Set environment variable BEFORE any imports that use storage
process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;

describe('Workflow Storage', () => {
  // Clean up before each test for isolation
  beforeEach(async () => {
    // Ensure env is set (in case of test parallelization)
    process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;
    // Clean previous test data
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
    await mkdir(TEST_STORAGE_ROOT, { recursive: true });
    await initWorkflowStorage();
  });

  afterEach(async () => {
    // Clean up after each test
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
  });

  describe('Workflow CRUD', () => {
    it('should create a workflow with basic info', async () => {
      const workflow = await createWorkflow({
        title: 'Test Workflow',
        description: 'A test workflow',
        project: 'test-project',
      });

      expect(workflow).toBeDefined();
      expect(workflow.id).toMatch(/^wf_/);
      expect(workflow.title).toBe('Test Workflow');
      expect(workflow.description).toBe('A test workflow');
      expect(workflow.project).toBe('test-project');
      expect(workflow.status).toBe('draft');
      expect(workflow.tasks).toHaveLength(0);
      expect(workflow.progress.percentage).toBe(0);
    });

    it('should create a workflow with initial tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Workflow with Tasks',
        tasks: [
          { title: 'Task 1', description: 'First task', priority: 'high' },
          { title: 'Task 2', description: 'Second task', priority: 'medium' },
          { title: 'Task 3', description: 'Third task', priority: 'low' },
        ],
      });

      expect(workflow.tasks).toHaveLength(3);
      expect(workflow.tasks[0].title).toBe('Task 1');
      expect(workflow.tasks[0].priority).toBe('high');
      expect(workflow.tasks[0].id).toMatch(/^task_/);
      expect(workflow.tasks[1].order).toBe(1);
      expect(workflow.progress.total).toBe(3);
    });

    it('should read a workflow by ID', async () => {
      const created = await createWorkflow({
        title: 'Read Test',
      });

      const read = await readWorkflow(created.id);

      expect(read).toBeDefined();
      expect(read!.id).toBe(created.id);
      expect(read!.title).toBe('Read Test');
    });

    it('should return null for non-existent workflow', async () => {
      const read = await readWorkflow('wf_nonexistent');
      expect(read).toBeNull();
    });

    it('should update workflow metadata', async () => {
      const created = await createWorkflow({
        title: 'Update Test',
        status: 'draft',
      });

      const updated = await updateWorkflow(created.id, {
        title: 'Updated Title',
        status: 'active',
        tags: ['test', 'updated'],
      });

      expect(updated).toBeDefined();
      expect(updated!.title).toBe('Updated Title');
      expect(updated!.status).toBe('active');
      expect(updated!.tags).toEqual(['test', 'updated']);
      expect(updated!.startedAt).toBeDefined(); // Set when status becomes 'active'
    });

    it('should delete a workflow', async () => {
      const created = await createWorkflow({
        title: 'Delete Test',
      });

      const deleted = await deleteWorkflow(created.id);
      expect(deleted).toBe(true);

      const read = await readWorkflow(created.id);
      expect(read).toBeNull();
    });

    it('should list workflows with filtering', async () => {
      await createWorkflow({ title: 'Project A', project: 'alpha', tags: ['urgent'] });
      await createWorkflow({ title: 'Project B', project: 'beta', tags: ['normal'] });
      await createWorkflow({ title: 'Project C', project: 'alpha', tags: ['urgent'] });

      // List all
      const all = await listWorkflows();
      expect(all).toHaveLength(3);

      // Filter by project
      const alphaOnly = await listWorkflows({ project: 'alpha' });
      expect(alphaOnly).toHaveLength(2);

      // Search
      const searchB = await listWorkflows({ search: 'Project B' });
      expect(searchB).toHaveLength(1);
      expect(searchB[0].title).toBe('Project B');
    });
  });

  describe('Task CRUD', () => {
    it('should add a task to a workflow', async () => {
      const workflow = await createWorkflow({ title: 'Task Test' });

      const task = await addTask(workflow.id, {
        title: 'New Task',
        description: 'Task description',
        priority: 'high',
      });

      expect(task).toBeDefined();
      expect(task!.id).toMatch(/^task_/);
      expect(task!.title).toBe('New Task');
      expect(task!.priority).toBe('high');
      expect(task!.status).toBe('pending');
    });

    it('should update a task', async () => {
      const workflow = await createWorkflow({
        title: 'Update Task Test',
        tasks: [{ title: 'Original', description: 'Original desc', priority: 'low' }],
      });

      const taskId = workflow.tasks[0].id;
      const updated = await updateTask(workflow.id, taskId, {
        title: 'Updated Task',
        status: 'in_progress',
      });

      expect(updated).toBeDefined();
      expect(updated!.title).toBe('Updated Task');
      expect(updated!.status).toBe('in_progress');
      expect(updated!.startedAt).toBeDefined();
    });

    it('should remove a task', async () => {
      const workflow = await createWorkflow({
        title: 'Remove Task Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      const removed = await removeTask(workflow.id, workflow.tasks[0].id);
      expect(removed).toBe(true);

      const updated = await readWorkflow(workflow.id);
      expect(updated!.tasks).toHaveLength(1);
      expect(updated!.tasks[0].title).toBe('Task 2');
      expect(updated!.tasks[0].order).toBe(0); // Re-ordered
    });

    it('should filter tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Filter Tasks Test',
        tasks: [
          { title: 'High Priority', description: '', priority: 'high' },
          { title: 'Low Priority', description: '', priority: 'low' },
          { title: 'Medium Priority', description: '', priority: 'medium' },
        ],
      });

      // Update one to in_progress
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });

      const inProgress = await getTasks(workflow.id, { status: 'in_progress' });
      expect(inProgress).toHaveLength(1);
      expect(inProgress[0].title).toBe('High Priority');

      const highPriority = await getTasks(workflow.id, { priority: 'high' });
      expect(highPriority).toHaveLength(1);
    });

    it('should complete a step within a task', async () => {
      const workflow = await createWorkflow({
        title: 'Step Test',
        tasks: [{
          title: 'Task with Steps',
          description: 'Has steps',
          steps: [
            { description: 'Step 1', estimatedMinutes: 5 },
            { description: 'Step 2', estimatedMinutes: 10 },
          ],
        }],
      });

      const taskId = workflow.tasks[0].id;
      const stepId = workflow.tasks[0].steps![0].id;

      const step = await completeStep(workflow.id, taskId, stepId, 'Done!');

      expect(step).toBeDefined();
      expect(step!.completed).toBe(true);
      expect(step!.completedAt).toBeDefined();
      expect(step!.evidence).toBe('Done!');
    });
  });

  describe('Progress Tracking', () => {
    it('should update progress when tasks are completed', async () => {
      const workflow = await createWorkflow({
        title: 'Progress Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
          { title: 'Task 3', description: '' },
          { title: 'Task 4', description: '' },
        ],
      });

      // Complete 2 tasks
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });
      await updateTask(workflow.id, workflow.tasks[1].id, { status: 'completed' });

      const updated = await readWorkflow(workflow.id);
      expect(updated!.progress.completed).toBe(2);
      expect(updated!.progress.percentage).toBe(50);
    });

    it('should track failed tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Failure Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'failed' });

      const updated = await readWorkflow(workflow.id);
      expect(updated!.progress.failed).toBe(1);
    });
  });

  describe('Event Sourcing', () => {
    it('should log events on workflow creation', async () => {
      const workflow = await createWorkflow({
        title: 'Event Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      const events = await readEvents(workflow.id);

      expect(events.length).toBeGreaterThan(0);
      expect(events[0].type).toBe('workflow_created');
      expect(events[0].workflowId).toBe(workflow.id);
    });

    it('should log events on status changes', async () => {
      const workflow = await createWorkflow({
        title: 'Status Event Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      const events = await readEvents(workflow.id);
      const taskEvents = events.filter(e => e.taskId === workflow.tasks[0].id);

      expect(taskEvents.length).toBeGreaterThanOrEqual(2);
    });

    it('should get recent events', async () => {
      const workflow = await createWorkflow({
        title: 'Recent Events Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
          { title: 'Task 3', description: '' },
        ],
      });

      // Generate some events
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });
      await updateTask(workflow.id, workflow.tasks[1].id, { status: 'in_progress' });

      const recent = await getRecentEvents(workflow.id, 3);

      expect(recent).toHaveLength(3);
      // Most recent should be last
      expect(recent[recent.length - 1].type).toBe('task_started');
    });
  });

  describe('Checkpoint Management', () => {
    it('should create a checkpoint', async () => {
      const workflow = await createWorkflow({
        title: 'Checkpoint Test',
        tasks: [{ title: 'Task 1', description: '' }],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'in_progress' });

      const checkpoint = await createCheckpoint(workflow.id, {
        notes: 'Checkpoint notes',
        reason: 'manual',
      });

      expect(checkpoint).toBeDefined();
      expect(checkpoint!.id).toMatch(/^cp_/);
      expect(checkpoint!.notes).toBe('Checkpoint notes');
      expect(checkpoint!.reason).toBe('manual');
      expect(checkpoint!.taskStatuses[workflow.tasks[0].id]).toBe('in_progress');
    });

    it('should list checkpoints', async () => {
      const workflow = await createWorkflow({
        title: 'List Checkpoints Test',
      });

      await createCheckpoint(workflow.id, { reason: 'manual' });
      await createCheckpoint(workflow.id, { reason: 'auto' });

      const checkpoints = await listCheckpoints(workflow.id);
      expect(checkpoints).toHaveLength(2);
    });

    it('should get latest checkpoint', async () => {
      const workflow = await createWorkflow({
        title: 'Latest Checkpoint Test',
      });

      await createCheckpoint(workflow.id, { notes: 'First' });
      // Small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 10));
      await createCheckpoint(workflow.id, { notes: 'Second' });

      const latest = await getLatestCheckpoint(workflow.id);
      expect(latest).toBeDefined();
      expect(latest!.notes).toBe('Second');
    });

    it('should restore from checkpoint', async () => {
      const workflow = await createWorkflow({
        title: 'Restore Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      // Complete task 1
      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });

      // Create checkpoint
      const checkpoint = await createCheckpoint(workflow.id);

      // Complete task 2
      await updateTask(workflow.id, workflow.tasks[1].id, { status: 'completed' });

      // Verify both completed
      let current = await readWorkflow(workflow.id);
      expect(current!.progress.completed).toBe(2);

      // Restore to checkpoint
      const restored = await restoreFromCheckpoint(workflow.id, checkpoint!.id);

      expect(restored).toBeDefined();
      expect(restored!.tasks[0].status).toBe('completed');
      expect(restored!.tasks[1].status).toBe('pending'); // Restored to pending
      expect(restored!.progress.completed).toBe(1);
    });
  });

  describe('Workflow Status Summary', () => {
    it('should return status summary', async () => {
      const workflow = await createWorkflow({
        title: 'Status Summary Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
          { title: 'Task 3', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'completed' });
      await updateTask(workflow.id, workflow.tasks[1].id, { status: 'in_progress' });

      const status = await getWorkflowStatus(workflow.id);

      expect(status).toBeDefined();
      expect(status!.workflow.title).toBe('Status Summary Test');
      expect(status!.workflow.progress.completed).toBe(1);
      expect(status!.currentTask).toBeDefined();
      expect(status!.currentTask!.title).toBe('Task 2');
      expect(status!.nextActions).toContain('Task 3');
    });

    it('should identify blocked tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Blocked Test',
        tasks: [
          { title: 'Blocked Task', description: '' },
        ],
      });

      await updateTask(workflow.id, workflow.tasks[0].id, { status: 'blocked' });

      const status = await getWorkflowStatus(workflow.id);

      expect(status!.blockers).toContain('Blocked Task');
    });
  });

  describe('Batch Execution', () => {
    it('should get next batch of tasks', async () => {
      const workflow = await createWorkflow({
        title: 'Batch Test',
        tasks: [
          { title: 'Task 1', description: '', priority: 'critical' },
          { title: 'Task 2', description: '', priority: 'high' },
          { title: 'Task 3', description: '', priority: 'medium' },
          { title: 'Task 4', description: '', priority: 'low' },
          { title: 'Task 5', description: '', priority: 'low' },
        ],
      });

      const batch = await getNextBatch(workflow.id, 3);

      expect(batch).toHaveLength(3);
      // Should be sorted by priority
      expect(batch[0].priority).toBe('critical');
      expect(batch[1].priority).toBe('high');
      expect(batch[2].priority).toBe('medium');
    });

    it('should respect task dependencies', async () => {
      const workflow = await createWorkflow({
        title: 'Dependency Test',
        tasks: [
          { title: 'Task A', description: '' },
          { title: 'Task B', description: '' },
        ],
      });

      // Add dependency: Task B depends on Task A
      await updateTask(workflow.id, workflow.tasks[1].id, {
        dependsOn: [workflow.tasks[0].id],
      });

      const batch = await getNextBatch(workflow.id, 2);

      // Only Task A should be eligible (Task B is blocked by dependency)
      expect(batch).toHaveLength(1);
      expect(batch[0].title).toBe('Task A');
    });

    it('should start a batch execution', async () => {
      const workflow = await createWorkflow({
        title: 'Start Batch Test',
        tasks: [
          { title: 'Task 1', description: '' },
          { title: 'Task 2', description: '' },
        ],
      });

      const batch = await startBatch(workflow.id);

      expect(batch).toBeDefined();
      expect(batch!.status).toBe('running');
      expect(batch!.taskIds).toHaveLength(2);

      // Verify tasks are now in_progress
      const updated = await readWorkflow(workflow.id);
      expect(updated!.tasks[0].status).toBe('in_progress');
      expect(updated!.tasks[1].status).toBe('in_progress');
      expect(updated!.status).toBe('active');
    });
  });
});
