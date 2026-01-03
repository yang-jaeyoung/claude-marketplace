#!/usr/bin/env node
/**
 * Magic Note MCP Server
 * Provides tools for Claude Code to manage notes
 *
 * Runtime Support:
 * - Bun: Primary runtime (fastest)
 * - Node.js 22.18+/23.6+: Native TypeScript support
 * - Node.js + tsx: Fallback for older Node.js versions
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

import {
  createNote,
  getNote,
  listNotes,
  updateNote,
  deleteNote,
  getAllTags,
  getAllProjects,
} from '../core/note.js';
import { listTemplates, getTemplate } from '../core/template.js';
import { isInitialized, initStorage } from '../core/storage.js';
import {
  createWorkflow,
  readWorkflow,
  updateWorkflow as updateWorkflowStorage,
  deleteWorkflow as deleteWorkflowStorage,
  listWorkflows,
  addTask,
  updateTask,
  removeTask,
  getTasks,
  createCheckpoint,
  listCheckpoints,
  restoreFromCheckpoint,
  getLatestCheckpoint,
  getWorkflowStatus,
  readEvents,
  getRecentEvents,
  initWorkflowStorage,
} from '../core/workflow-storage.js';
import { VERSION, NAME } from '../core/version.js';
import { logRuntimeInfo } from '../core/runtime.js';
import type {
  NoteType,
  NoteFilter,
  CreateNoteInput,
  WorkflowStatus,
  TaskStatus,
  TaskPriority,
  WorkflowEvent,
  Workflow,
  Task,
} from '../core/types.js';

// Create MCP server
const server = new McpServer({
  name: NAME,
  version: VERSION,
});

// Helper to ensure storage is initialized
async function ensureInit() {
  if (!(await isInitialized())) {
    await initStorage();
  }
  // Also ensure workflow storage is initialized
  await initWorkflowStorage();
}

// ============================================================================
// HELPER FUNCTIONS FOR WORKFLOW TOOLS
// ============================================================================

// Progress bar builder
function buildProgressBar(percent: number): string {
  const filled = Math.round(percent / 6.25);
  const empty = 16 - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

// Relative time formatter
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

// Event emoji mapper
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

// Status emoji mapper
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

// Format event for display
function formatEventLine(event: WorkflowEvent): string {
  const time = new Date(event.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  const emoji = getEventEmoji(event.type);
  const description = event.payload.title || event.type.replace(/_/g, ' ');
  return `  ${time} ${emoji} ${description}`;
}

// Register tools using registerTool API

// list_notes - List all notes with optional filtering
server.registerTool(
  'list_notes',
  {
    title: 'List Notes',
    description: 'List all notes with optional filtering by type, project, or tags',
    inputSchema: {
      type: z.enum(['prompt', 'plan', 'choice', 'insight']).optional().describe('Filter by note type'),
      project: z.string().optional().describe('Filter by project name'),
      tags: z.array(z.string()).optional().describe('Filter by tags'),
      search: z.string().optional().describe('Search in title and tags'),
    },
  },
  async ({ type, project, tags, search }) => {
    await ensureInit();

    const filter: NoteFilter = {};
    if (type) filter.type = type as NoteType;
    if (project) filter.project = project;
    if (tags) filter.tags = tags;
    if (search) filter.search = search;

    const notes = await listNotes(filter);
    return {
      content: [{ type: 'text', text: JSON.stringify(notes, null, 2) }],
    };
  }
);

// get_note - Get a specific note by ID
server.registerTool(
  'get_note',
  {
    title: 'Get Note',
    description: 'Get a specific note by ID with full content',
    inputSchema: {
      id: z.string().describe('Note ID'),
    },
  },
  async ({ id }) => {
    await ensureInit();

    const note = await getNote(id);
    if (!note) {
      return {
        content: [{ type: 'text', text: `Note not found: ${id}` }],
        isError: true,
      };
    }
    return {
      content: [{ type: 'text', text: JSON.stringify(note, null, 2) }],
    };
  }
);

// add_note - Create a new note
server.registerTool(
  'add_note',
  {
    title: 'Add Note',
    description: 'Create a new note',
    inputSchema: {
      type: z.enum(['prompt', 'plan', 'choice', 'insight']).describe('Note type'),
      title: z.string().describe('Note title'),
      content: z.string().describe('Note content'),
      tags: z.array(z.string()).optional().describe('Tags for the note'),
      project: z.string().optional().describe('Project name'),
    },
  },
  async ({ type, title, content, tags, project }) => {
    await ensureInit();

    const input: CreateNoteInput = {
      type: type as NoteType,
      title,
      content,
      tags: tags || [],
      project,
    };

    const note = await createNote(input);
    return {
      content: [
        {
          type: 'text',
          text: `Note created successfully!\nID: ${note.id}\nTitle: ${note.title}`,
        },
      ],
    };
  }
);

// update_note - Update an existing note
server.registerTool(
  'update_note',
  {
    title: 'Update Note',
    description: 'Update an existing note',
    inputSchema: {
      id: z.string().describe('Note ID'),
      title: z.string().optional().describe('New title'),
      content: z.string().optional().describe('New content'),
      tags: z.array(z.string()).optional().describe('New tags'),
    },
  },
  async ({ id, title, content, tags }) => {
    await ensureInit();

    const updated = await updateNote(id, { title, content, tags });

    if (!updated) {
      return {
        content: [{ type: 'text', text: `Note not found: ${id}` }],
        isError: true,
      };
    }

    return {
      content: [
        { type: 'text', text: `Note updated successfully!\nID: ${updated.id}` },
      ],
    };
  }
);

// delete_note - Delete a note by ID
server.registerTool(
  'delete_note',
  {
    title: 'Delete Note',
    description: 'Delete a note by ID',
    inputSchema: {
      id: z.string().describe('Note ID to delete'),
    },
  },
  async ({ id }) => {
    await ensureInit();

    const success = await deleteNote(id);
    return {
      content: [
        {
          type: 'text',
          text: success ? `Note deleted: ${id}` : `Failed to delete note: ${id}`,
        },
      ],
      isError: !success,
    };
  }
);

// upsert_insight - Add insight to project's insight note (create or update)
server.registerTool(
  'upsert_insight',
  {
    title: 'Upsert Insight',
    description: 'Add an insight to the project insight note. Creates new note if none exists, or appends to existing one.',
    inputSchema: {
      project: z.string().describe('Project name (usually from current working directory)'),
      insight: z.string().describe('The insight content to add'),
      context: z.string().optional().describe('Optional context about when/why this insight was generated'),
      tags: z.array(z.string()).optional().describe('Additional tags for the insight'),
    },
  },
  async ({ project, insight, context, tags }) => {
    await ensureInit();

    // Search for existing insight note for this project
    const existingNotes = await listNotes({
      type: 'insight' as NoteType,
      project
    });

    const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const timeStr = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

    // Format new insight entry
    const newInsightEntry = context
      ? `### ${timestamp} ${timeStr}\n**Context**: ${context}\n\n${insight}\n\n---\n`
      : `### ${timestamp} ${timeStr}\n\n${insight}\n\n---\n`;

    if (existingNotes.length > 0) {
      // Update existing insight note
      const existingNote = await getNote(existingNotes[0].id);
      if (existingNote) {
        const updatedContent = existingNote.content + '\n' + newInsightEntry;
        const existingTags = existingNote.tags || [];
        const newTags = tags || [];
        const mergedTags = [...new Set([...existingTags, ...newTags])];

        await updateNote(existingNote.id, {
          content: updatedContent,
          tags: mergedTags
        });

        return {
          content: [
            {
              type: 'text',
              text: `💡 Insight added to existing note!\nProject: ${project}\nNote ID: ${existingNote.id}\nTotal insights: ${(updatedContent.match(/^### \d{4}-\d{2}-\d{2}/gm) || []).length}`,
            },
          ],
        };
      }
    }

    // Create new insight note for this project
    const initialContent = `# ${project} - Insights Collection\n\n` +
      `> 이 프로젝트에서 학습한 인사이트 모음\n\n` +
      `---\n\n` +
      newInsightEntry;

    const note = await createNote({
      type: 'insight' as NoteType,
      title: `${project} Insights`,
      content: initialContent,
      tags: ['insight', 'auto-captured', ...(tags || [])],
      project,
    });

    return {
      content: [
        {
          type: 'text',
          text: `💡 New insight note created!\nProject: ${project}\nNote ID: ${note.id}`,
        },
      ],
    };
  }
);

// list_templates - List all available templates
server.registerTool(
  'list_templates',
  {
    title: 'List Templates',
    description: 'List all available templates',
    inputSchema: {},
  },
  async () => {
    await ensureInit();

    const templates = await listTemplates();
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(
            templates.map((t) => ({
              name: t.name,
              type: t.type,
              description: t.description,
              tags: t.tags,
            })),
            null,
            2
          ),
        },
      ],
    };
  }
);

// use_template - Create a note from a template
server.registerTool(
  'use_template',
  {
    title: 'Use Template',
    description: 'Create a note from a template',
    inputSchema: {
      templateName: z.string().describe('Template name'),
      title: z.string().describe('Note title'),
      project: z.string().optional().describe('Project name'),
    },
  },
  async ({ templateName, title, project }) => {
    await ensureInit();

    const template = await getTemplate(templateName);
    if (!template) {
      return {
        content: [{ type: 'text', text: `Template not found: ${templateName}` }],
        isError: true,
      };
    }

    let content = template.content;
    content = content.replace(/\{\{\s*title\s*\}\}/g, title);

    const note = await createNote({
      type: template.type,
      title,
      content,
      tags: template.tags,
      project,
    });

    return {
      content: [
        {
          type: 'text',
          text: `Note created from template!\nID: ${note.id}\nTitle: ${note.title}`,
        },
      ],
    };
  }
);

// list_projects - List all projects
server.registerTool(
  'list_projects',
  {
    title: 'List Projects',
    description: 'List all projects',
    inputSchema: {},
  },
  async () => {
    await ensureInit();

    const projects = await getAllProjects();
    return {
      content: [{ type: 'text', text: JSON.stringify(projects, null, 2) }],
    };
  }
);

// list_tags - List all unique tags
server.registerTool(
  'list_tags',
  {
    title: 'List Tags',
    description: 'List all unique tags',
    inputSchema: {},
  },
  async () => {
    await ensureInit();

    const tags = await getAllTags();
    return {
      content: [{ type: 'text', text: JSON.stringify(tags, null, 2) }],
    };
  }
);

// ============================================================================
// WORKFLOW MANAGEMENT TOOLS (6)
// ============================================================================

// create_workflow - Create a new workflow
server.registerTool(
  'create_workflow',
  {
    title: 'Create Workflow',
    description: 'Create a new workflow for managing a multi-step task or project',
    inputSchema: {
      title: z.string().describe('Workflow title'),
      description: z.string().optional().describe('Detailed description'),
      project: z.string().optional().describe('Project/workspace name'),
      tasks: z.array(z.object({
        title: z.string(),
        description: z.string().optional(),
        priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
      })).optional().describe('Initial tasks to add'),
      planNoteId: z.string().optional().describe('Create from existing plan note ID'),
      tags: z.array(z.string()).optional().describe('Tags for the workflow'),
    },
  },
  async ({ title, description, project, tasks, planNoteId, tags }) => {
    await ensureInit();

    const workflow = await createWorkflow({
      title,
      description,
      project,
      planNoteId,
      tags,
      tasks: tasks?.map((t, i) => ({
        title: t.title,
        description: t.description || '',
        priority: (t.priority as TaskPriority) || 'medium',
        order: i,
      })),
    });

    return {
      content: [{
        type: 'text',
        text: `📋 Workflow created!\nID: ${workflow.id}\nTitle: ${workflow.title}\nTasks: ${workflow.tasks.length}`,
      }],
    };
  }
);

// get_workflow - Get workflow details
server.registerTool(
  'get_workflow',
  {
    title: 'Get Workflow',
    description: 'Get detailed information about a workflow including all tasks',
    inputSchema: {
      id: z.string().describe('Workflow ID'),
      includeTasks: z.boolean().optional().default(true).describe('Include task details'),
      includeEvents: z.boolean().optional().default(false).describe('Include recent events'),
      eventLimit: z.number().optional().default(10).describe('Number of events to include'),
    },
  },
  async ({ id, includeTasks, includeEvents, eventLimit }) => {
    await ensureInit();

    const workflow = await readWorkflow(id);
    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${id}` }],
        isError: true,
      };
    }

    const result: Record<string, unknown> = {
      id: workflow.id,
      title: workflow.title,
      description: workflow.description,
      status: workflow.status,
      project: workflow.project,
      progress: workflow.progress,
      createdAt: workflow.createdAt,
      updatedAt: workflow.updatedAt,
      tags: workflow.tags,
    };

    if (includeTasks) {
      result.tasks = workflow.tasks;
    }

    if (includeEvents) {
      result.recentEvents = await getRecentEvents(id, eventLimit);
    }

    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  }
);

// list_workflows - List workflows with filtering
server.registerTool(
  'list_workflows',
  {
    title: 'List Workflows',
    description: 'List workflows with optional filtering',
    inputSchema: {
      project: z.string().optional().describe('Filter by project'),
      status: z.enum(['draft', 'ready', 'active', 'paused', 'blocked', 'completed', 'failed', 'cancelled']).optional().describe('Filter by status'),
      activeOnly: z.boolean().optional().default(false).describe('Show only active workflows'),
      search: z.string().optional().describe('Search in title'),
      limit: z.number().optional().default(20).describe('Maximum results'),
    },
  },
  async ({ project, status, activeOnly, search, limit }) => {
    await ensureInit();

    const workflows = await listWorkflows({
      project,
      status: activeOnly ? 'active' : status as WorkflowStatus,
      search,
    });

    const limited = workflows.slice(0, limit);

    // Format for display
    const formatted = limited.map(w => ({
      id: w.id,
      title: w.title,
      status: w.status,
      progress: `${w.progress.percentage}%`,
      updated: formatRelativeTime(w.updatedAt),
    }));

    return {
      content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }],
    };
  }
);

// update_workflow - Update workflow metadata
server.registerTool(
  'update_workflow',
  {
    title: 'Update Workflow',
    description: 'Update workflow metadata (title, description, status)',
    inputSchema: {
      id: z.string().describe('Workflow ID'),
      title: z.string().optional().describe('New title'),
      description: z.string().optional().describe('New description'),
      status: z.enum(['draft', 'ready', 'active', 'paused', 'blocked', 'completed', 'failed', 'cancelled']).optional().describe('New status'),
      tags: z.array(z.string()).optional().describe('New tags'),
    },
  },
  async ({ id, title, description, status, tags }) => {
    await ensureInit();

    const workflow = await updateWorkflowStorage(id, {
      title,
      description,
      status: status as WorkflowStatus,
      tags,
    });

    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${id}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `✅ Workflow updated!\nID: ${workflow.id}\nStatus: ${workflow.status}`,
      }],
    };
  }
);

// delete_workflow - Delete a workflow
server.registerTool(
  'delete_workflow',
  {
    title: 'Delete Workflow',
    description: 'Delete a workflow and all its data',
    inputSchema: {
      id: z.string().describe('Workflow ID to delete'),
    },
  },
  async ({ id }) => {
    await ensureInit();

    const success = await deleteWorkflowStorage(id);

    return {
      content: [{
        type: 'text',
        text: success ? `🗑️ Workflow deleted: ${id}` : `Failed to delete workflow: ${id}`,
      }],
      isError: !success,
    };
  }
);

// archive_workflow - Archive a workflow (set status to completed)
server.registerTool(
  'archive_workflow',
  {
    title: 'Archive Workflow',
    description: 'Archive a completed workflow',
    inputSchema: {
      id: z.string().describe('Workflow ID to archive'),
    },
  },
  async ({ id }) => {
    await ensureInit();

    const workflow = await updateWorkflowStorage(id, { status: 'completed' });

    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${id}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `📦 Workflow archived: ${workflow.title}`,
      }],
    };
  }
);

// ============================================================================
// TASK MANAGEMENT TOOLS (6)
// ============================================================================

// add_task - Add a task to a workflow
server.registerTool(
  'add_task',
  {
    title: 'Add Task',
    description: 'Add a new task to a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      title: z.string().describe('Task title'),
      description: z.string().optional().describe('Task description'),
      priority: z.enum(['low', 'medium', 'high', 'critical']).optional().default('medium').describe('Task priority'),
      dependsOn: z.array(z.string()).optional().describe('IDs of tasks this depends on'),
      noteIds: z.array(z.string()).optional().describe('Related note IDs'),
    },
  },
  async ({ workflowId, title, description, priority, dependsOn, noteIds }) => {
    await ensureInit();

    const task = await addTask(workflowId, {
      title,
      description: description || '',
      priority: priority as TaskPriority,
      dependsOn,
      noteIds,
    });

    if (!task) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `➕ Task added!\nID: ${task.id}\nTitle: ${task.title}`,
      }],
    };
  }
);

// update_task - Update a task
server.registerTool(
  'update_task',
  {
    title: 'Update Task',
    description: 'Update task details',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().describe('Task ID'),
      title: z.string().optional().describe('New title'),
      description: z.string().optional().describe('New description'),
      priority: z.enum(['low', 'medium', 'high', 'critical']).optional().describe('New priority'),
      tags: z.array(z.string()).optional().describe('New tags'),
    },
  },
  async ({ workflowId, taskId, title, description, priority, tags }) => {
    await ensureInit();

    const task = await updateTask(workflowId, taskId, {
      title,
      description,
      priority: priority as TaskPriority,
      tags,
    });

    if (!task) {
      return {
        content: [{ type: 'text', text: `Task not found: ${taskId}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `✅ Task updated: ${task.title}`,
      }],
    };
  }
);

// remove_task - Remove a task
server.registerTool(
  'remove_task',
  {
    title: 'Remove Task',
    description: 'Remove a task from a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().describe('Task ID to remove'),
    },
  },
  async ({ workflowId, taskId }) => {
    await ensureInit();

    const success = await removeTask(workflowId, taskId);

    return {
      content: [{
        type: 'text',
        text: success ? `🗑️ Task removed: ${taskId}` : `Failed to remove task: ${taskId}`,
      }],
      isError: !success,
    };
  }
);

// reorder_tasks - Reorder tasks in a workflow
server.registerTool(
  'reorder_tasks',
  {
    title: 'Reorder Tasks',
    description: 'Reorder tasks by providing new order',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      taskIds: z.array(z.string()).describe('Task IDs in new order'),
    },
  },
  async ({ workflowId, taskIds }) => {
    await ensureInit();

    // Update each task's order
    for (let i = 0; i < taskIds.length; i++) {
      await updateTask(workflowId, taskIds[i], { order: i });
    }

    return {
      content: [{
        type: 'text',
        text: `📋 Tasks reordered: ${taskIds.length} tasks`,
      }],
    };
  }
);

// set_task_status - Change task status (Core Tool ⭐)
server.registerTool(
  'set_task_status',
  {
    title: 'Set Task Status',
    description: 'Change the status of a task (start, complete, block, etc.)',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().describe('Task ID'),
      status: z.enum(['pending', 'in_progress', 'verifying', 'review', 'completed', 'failed', 'skipped', 'blocked']).describe('New status'),
      note: z.string().optional().describe('Note about this status change'),
    },
  },
  async ({ workflowId, taskId, status, note }) => {
    await ensureInit();

    const task = await updateTask(workflowId, taskId, {
      status: status as TaskStatus,
    });

    if (!task) {
      return {
        content: [{ type: 'text', text: `Task not found: ${taskId}` }],
        isError: true,
      };
    }

    const emoji = getStatusEmoji(status as TaskStatus);
    let message = `${emoji} Task status updated: ${task.title} → ${status}`;
    if (note) {
      message += `\nNote: ${note}`;
    }

    return {
      content: [{ type: 'text', text: message }],
    };
  }
);

// delegate_task - Delegate a task to an agent
server.registerTool(
  'delegate_task',
  {
    title: 'Delegate Task',
    description: 'Delegate a task to a specialized agent for autonomous execution',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().describe('Task ID'),
      agentType: z.string().describe('Agent type (e.g., "code-reviewer", "test-runner")'),
      instructions: z.string().optional().describe('Additional instructions for the agent'),
    },
  },
  async ({ workflowId, taskId, agentType, instructions }) => {
    await ensureInit();

    // Update task with delegation info
    const task = await updateTask(workflowId, taskId, {
      status: 'in_progress',
    });

    if (!task) {
      return {
        content: [{ type: 'text', text: `Task not found: ${taskId}` }],
        isError: true,
      };
    }

    // Note: Actual delegation would happen through Claude's Task tool
    // This just marks the task as delegated
    return {
      content: [{
        type: 'text',
        text: `🤖 Task delegated to ${agentType}\nTask: ${task.title}\n${instructions ? `Instructions: ${instructions}` : ''}`,
      }],
    };
  }
);

// ============================================================================
// CHECKPOINT MANAGEMENT TOOLS (3)
// ============================================================================

// create_checkpoint - Create a checkpoint
server.registerTool(
  'create_checkpoint',
  {
    title: 'Create Checkpoint',
    description: 'Create a checkpoint to save current workflow state',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      notes: z.string().optional().describe('Summary of current state'),
      reason: z.enum(['manual', 'milestone', 'session_end']).optional().default('manual').describe('Reason for checkpoint'),
    },
  },
  async ({ workflowId, notes, reason }) => {
    await ensureInit();

    const checkpoint = await createCheckpoint(workflowId, {
      notes,
      reason: reason as 'manual' | 'auto' | 'session_end' | 'phase_complete',
    });

    if (!checkpoint) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `📸 Checkpoint created!\nID: ${checkpoint.id}\nReason: ${checkpoint.reason}`,
      }],
    };
  }
);

// list_checkpoints - List checkpoints
server.registerTool(
  'list_checkpoints',
  {
    title: 'List Checkpoints',
    description: 'List all checkpoints for a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
    },
  },
  async ({ workflowId }) => {
    await ensureInit();

    const checkpoints = await listCheckpoints(workflowId);

    const formatted = checkpoints.map(cp => ({
      id: cp.id,
      reason: cp.reason,
      notes: cp.notes,
      created: formatRelativeTime(cp.createdAt),
    }));

    return {
      content: [{ type: 'text', text: JSON.stringify(formatted, null, 2) }],
    };
  }
);

// restore_checkpoint - Restore from checkpoint
server.registerTool(
  'restore_checkpoint',
  {
    title: 'Restore Checkpoint',
    description: 'Restore workflow state from a checkpoint',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      checkpointId: z.string().describe('Checkpoint ID to restore'),
    },
  },
  async ({ workflowId, checkpointId }) => {
    await ensureInit();

    const workflow = await restoreFromCheckpoint(workflowId, checkpointId);

    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Checkpoint not found: ${checkpointId}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text',
        text: `⏪ Restored from checkpoint!\nWorkflow: ${workflow.title}\nProgress: ${workflow.progress.percentage}%`,
      }],
    };
  }
);

// ============================================================================
// ARTIFACT LINKING TOOLS (2)
// ============================================================================

// link_artifact - Link a note to a workflow/task
server.registerTool(
  'link_artifact',
  {
    title: 'Link Artifact',
    description: 'Link a note as an artifact to a workflow or task',
    inputSchema: {
      noteId: z.string().describe('Note ID to link'),
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().optional().describe('Optional: specific task ID'),
      role: z.enum(['definition', 'reference', 'output', 'decision', 'learning']).optional().describe('Role of the artifact'),
    },
  },
  async ({ noteId, workflowId, taskId, role }) => {
    await ensureInit();

    // Verify note exists
    const note = await getNote(noteId);
    if (!note) {
      return {
        content: [{ type: 'text', text: `Note not found: ${noteId}` }],
        isError: true,
      };
    }

    const workflow = await readWorkflow(workflowId);
    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    if (taskId) {
      // Link to specific task
      const task = workflow.tasks.find(t => t.id === taskId);
      if (!task) {
        return {
          content: [{ type: 'text', text: `Task not found: ${taskId}` }],
          isError: true,
        };
      }

      // Add note ID to task's noteIds
      if (!task.noteIds) task.noteIds = [];
      if (!task.noteIds.includes(noteId)) {
        task.noteIds.push(noteId);
        await updateTask(workflowId, taskId, {});
      }
    } else {
      // Link to workflow
      if (!workflow.relatedNoteIds) workflow.relatedNoteIds = [];
      if (!workflow.relatedNoteIds.includes(noteId)) {
        workflow.relatedNoteIds.push(noteId);
        await updateWorkflowStorage(workflowId, {});
      }
    }

    return {
      content: [{
        type: 'text',
        text: `🔗 Artifact linked!\nNote: ${note.title}\n${taskId ? `Task: ${taskId}` : `Workflow: ${workflowId}`}${role ? `\nRole: ${role}` : ''}`,
      }],
    };
  }
);

// unlink_artifact - Unlink a note from workflow/task
server.registerTool(
  'unlink_artifact',
  {
    title: 'Unlink Artifact',
    description: 'Unlink a note from a workflow or task',
    inputSchema: {
      noteId: z.string().describe('Note ID to unlink'),
      workflowId: z.string().describe('Workflow ID'),
      taskId: z.string().optional().describe('Optional: specific task ID'),
    },
  },
  async ({ noteId, workflowId, taskId }) => {
    await ensureInit();

    const workflow = await readWorkflow(workflowId);
    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    if (taskId) {
      const task = workflow.tasks.find(t => t.id === taskId);
      if (task?.noteIds) {
        task.noteIds = task.noteIds.filter(id => id !== noteId);
        await updateTask(workflowId, taskId, {});
      }
    } else {
      if (workflow.relatedNoteIds) {
        workflow.relatedNoteIds = workflow.relatedNoteIds.filter(id => id !== noteId);
        await updateWorkflowStorage(workflowId, {});
      }
    }

    return {
      content: [{
        type: 'text',
        text: `🔓 Artifact unlinked: ${noteId}`,
      }],
    };
  }
);

// ============================================================================
// QUERY & INSIGHTS TOOLS (3)
// ============================================================================

// get_workflow_status - Get human-readable status summary (Core Tool ⭐)
server.registerTool(
  'get_workflow_status',
  {
    title: 'Get Workflow Status',
    description: 'Get a human-readable summary of workflow progress',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      format: z.enum(['summary', 'detailed', 'minimal']).optional().default('summary').describe('Output format'),
    },
  },
  async ({ workflowId, format }) => {
    await ensureInit();

    const status = await getWorkflowStatus(workflowId);
    if (!status) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    const workflow = await readWorkflow(workflowId);
    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    if (format === 'minimal') {
      return {
        content: [{
          type: 'text',
          text: `${status.workflow.title}: ${status.workflow.progress.percentage}% (${status.workflow.status})`,
        }],
      };
    }

    // Build summary output
    let output = `📋 ${status.workflow.title}\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    output += `Progress: ${buildProgressBar(status.workflow.progress.percentage)} ${status.workflow.progress.percentage}%\n\n`;

    // Current task
    if (status.currentTask) {
      output += `🔄 In Progress:\n`;
      output += `   • ${status.currentTask.title}\n`;
      if (status.currentTask.currentStep) {
        output += `     └─ Step: ${status.currentTask.currentStep.description}\n`;
      }
      output += '\n';
    }

    // Blocked tasks
    if (status.blockers.length > 0) {
      output += `❌ Blocked:\n`;
      status.blockers.forEach(b => {
        output += `   • ${b}\n`;
      });
      output += '\n';
    }

    // Next tasks
    if (status.nextActions.length > 0) {
      output += `⏳ Next:\n`;
      status.nextActions.forEach(a => {
        output += `   • ${a}\n`;
      });
      output += '\n';
    }

    if (format === 'detailed') {
      // Add all tasks with status
      output += `📝 All Tasks:\n`;
      workflow.tasks.forEach(task => {
        output += `   ${getStatusEmoji(task.status)} ${task.title}\n`;
      });
      output += '\n';
    }

    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    output += `Status: ${status.workflow.status} | Updated: ${formatRelativeTime(workflow.updatedAt)}`;

    return {
      content: [{ type: 'text', text: output }],
    };
  }
);

// resume_workflow - Get context to resume work (Core Tool ⭐)
server.registerTool(
  'resume_workflow',
  {
    title: 'Resume Workflow',
    description: 'Get context to resume work - shows where you left off',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
    },
  },
  async ({ workflowId }) => {
    await ensureInit();

    const workflow = await readWorkflow(workflowId);
    if (!workflow) {
      return {
        content: [{ type: 'text', text: `Workflow not found: ${workflowId}` }],
        isError: true,
      };
    }

    const status = await getWorkflowStatus(workflowId);
    const checkpoint = await getLatestCheckpoint(workflowId);
    const events = await getRecentEvents(workflowId, 5);

    let output = `👋 Resume: ${workflow.title}\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    // Last checkpoint
    if (checkpoint) {
      output += `📸 Last checkpoint: ${formatRelativeTime(checkpoint.createdAt)}\n`;
      if (checkpoint.notes) {
        output += `   ${checkpoint.notes}\n`;
      }
      output += '\n';
    }

    // Progress
    output += `📊 Progress: ${buildProgressBar(workflow.progress.percentage)} ${workflow.progress.percentage}%\n\n`;

    // Last completed task
    const completedTasks = workflow.tasks
      .filter(t => t.status === 'completed' && t.completedAt)
      .sort((a, b) => new Date(b.completedAt!).getTime() - new Date(a.completedAt!).getTime());

    if (completedTasks.length > 0) {
      const last = completedTasks[0];
      output += `✅ Last completed: ${last.title}\n`;
      output += `   (${formatRelativeTime(last.completedAt!)})\n\n`;
    }

    // Current task
    if (status?.currentTask) {
      output += `🔄 Continue working on:\n`;
      output += `   → ${status.currentTask.title}\n`;
      const task = workflow.tasks.find(t => t.id === status.currentTask!.id);
      if (task?.description) {
        output += `     ${task.description.slice(0, 100)}...\n`;
      }
      output += '\n';
    }

    // Next tasks
    if (status && status.nextActions.length > 0) {
      output += `⏳ Next up:\n`;
      status.nextActions.forEach((a, i) => {
        output += `   ${i + 1}. ${a}\n`;
      });
      output += '\n';
    }

    // Recent activity
    if (events.length > 0) {
      output += `📝 Recent activity:\n`;
      // Group by date
      const today = new Date().toDateString();
      events.forEach(event => {
        const eventDate = new Date(event.timestamp).toDateString();
        const prefix = eventDate === today ? '' : `[${eventDate}] `;
        output += `   ${prefix}${getEventEmoji(event.type)} ${event.type.replace(/_/g, ' ')}\n`;
      });
      output += '\n';
    }

    // Linked notes
    if (workflow.relatedNoteIds && workflow.relatedNoteIds.length > 0) {
      output += `📎 Linked notes: ${workflow.relatedNoteIds.length}\n\n`;
    }

    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    output += `Quick actions:\n`;
    output += `  • set_task_status to update progress\n`;
    output += `  • create_checkpoint to save state\n`;
    output += `  • get_timeline for full history`;

    return {
      content: [{ type: 'text', text: output }],
    };
  }
);

// get_timeline - Get event timeline
server.registerTool(
  'get_timeline',
  {
    title: 'Get Timeline',
    description: 'Get the event timeline for a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      limit: z.number().optional().default(20).describe('Maximum events to return'),
      eventTypes: z.array(z.string()).optional().describe('Filter by event types'),
    },
  },
  async ({ workflowId, limit, eventTypes }) => {
    await ensureInit();

    let events = await readEvents(workflowId);

    // Filter by event types if specified
    if (eventTypes && eventTypes.length > 0) {
      events = events.filter(e => eventTypes.includes(e.type));
    }

    // Take last N events
    events = events.slice(-limit);

    // Group by date
    const grouped: Record<string, WorkflowEvent[]> = {};
    events.forEach(event => {
      const date = new Date(event.timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
      if (!grouped[date]) grouped[date] = [];
      grouped[date].push(event);
    });

    let output = `📜 Timeline: ${workflowId}\n`;
    output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    Object.entries(grouped)
      .sort((a, b) => new Date(b[0]).getTime() - new Date(a[0]).getTime())
      .forEach(([date, dayEvents]) => {
        output += `📅 ${date}\n`;
        dayEvents
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          .forEach(event => {
            output += formatEventLine(event) + '\n';
          });
        output += '\n';
      });

    return {
      content: [{ type: 'text', text: output }],
    };
  }
);

// Start server
async function main() {
  logRuntimeInfo();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[magic-note] MCP server running');
}

main().catch(console.error);
