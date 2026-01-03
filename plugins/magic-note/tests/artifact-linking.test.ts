/**
 * Integration test for artifact linking fix (#11)
 */
import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { mkdir, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';
import {
  createWorkflow,
  readWorkflow,
  updateWorkflow,
  updateTask,
  initWorkflowStorage,
} from '../src/core/workflow-storage';

const TEST_STORAGE_ROOT = join(homedir(), '.magic-note-test-artifact');
process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;

describe('Artifact Linking Fix (#11)', () => {
  beforeEach(async () => {
    process.env.MAGIC_NOTE_STORAGE = TEST_STORAGE_ROOT;
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
    await mkdir(TEST_STORAGE_ROOT, { recursive: true });
    await initWorkflowStorage();
  });

  afterEach(async () => {
    await rm(TEST_STORAGE_ROOT, { recursive: true, force: true });
  });

  it('should persist relatedNoteIds on workflow', async () => {
    const workflow = await createWorkflow({
      title: 'Artifact Link Test',
      tasks: [{ title: 'Task 1', description: 'Test task' }],
    });

    // Link a note to the workflow
    const updated = await updateWorkflow(workflow.id, {
      relatedNoteIds: ['note_123', 'note_456'],
    });

    expect(updated).not.toBeNull();
    expect(updated!.relatedNoteIds).toEqual(['note_123', 'note_456']);

    // Verify persistence
    const reloaded = await readWorkflow(workflow.id);
    expect(reloaded!.relatedNoteIds).toEqual(['note_123', 'note_456']);
  });

  it('should persist noteIds on task', async () => {
    const workflow = await createWorkflow({
      title: 'Task Artifact Link Test',
      tasks: [{ title: 'Task 1', description: 'Test task' }],
    });

    const taskId = workflow.tasks[0].id;

    // Link notes to the task
    const updated = await updateTask(workflow.id, taskId, {
      noteIds: ['note_abc', 'note_def'],
    });

    expect(updated).not.toBeNull();
    expect(updated!.noteIds).toEqual(['note_abc', 'note_def']);

    // Verify persistence
    const reloaded = await readWorkflow(workflow.id);
    expect(reloaded!.tasks[0].noteIds).toEqual(['note_abc', 'note_def']);
  });
});
