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
import { VERSION, NAME } from '../core/version.js';
import { logRuntimeInfo } from '../core/runtime.js';
import type { NoteType, NoteFilter, CreateNoteInput } from '../core/types.js';

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

// Start server
async function main() {
  logRuntimeInfo();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[magic-note] MCP server running');
}

main().catch(console.error);
