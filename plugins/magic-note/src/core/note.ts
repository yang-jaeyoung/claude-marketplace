/**
 * Note CRUD operations
 */

import matter from 'gray-matter';
import { nanoid } from 'nanoid';
import type {
  Note,
  NoteMeta,
  NoteType,
  CreateNoteInput,
  UpdateNoteInput,
  NoteFilter,
  IndexEntry,
} from './types';
import {
  getNotePath,
  ensureProjectDir,
  readFileContent,
  writeFileContent,
  deleteFile,
  fileExists,
  readIndex,
  writeIndex,
  listProjectDirs,
  listNoteFiles,
} from './storage';
import { readConfig } from './config';

// Generate unique note ID
function generateNoteId(): string {
  return nanoid(10);
}

// Valid note types for validation
const VALID_NOTE_TYPES = ['prompt', 'plan', 'choice'] as const;
const VALID_FORMATS = ['markdown', 'text', 'xml', 'yaml'] as const;

// Validate and sanitize string
function safeString(value: unknown, defaultValue: string): string {
  if (typeof value === 'string' && value.length <= 1000) {
    return value;
  }
  return defaultValue;
}

// Validate and sanitize string array
function safeStringArray(value: unknown, maxItems = 50): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === 'string' && item.length <= 100)
    .slice(0, maxItems);
}

// Validate note type
function safeNoteType(value: unknown): NoteType {
  if (typeof value === 'string' && VALID_NOTE_TYPES.includes(value as NoteType)) {
    return value as NoteType;
  }
  return 'prompt';
}

// Validate content format
function safeFormat(value: unknown): 'markdown' | 'text' | 'xml' | 'yaml' {
  if (typeof value === 'string' && VALID_FORMATS.includes(value as typeof VALID_FORMATS[number])) {
    return value as typeof VALID_FORMATS[number];
  }
  return 'markdown';
}

// Validate ISO date string
function safeISODate(value: unknown): string {
  if (typeof value === 'string') {
    const date = new Date(value);
    if (!isNaN(date.getTime())) {
      return value;
    }
  }
  return new Date().toISOString();
}

// Parse note file content to Note object with validation
function parseNoteFile(content: string, id: string): Note {
  const { data, content: body } = matter(content);

  return {
    id,
    type: safeNoteType(data.type),
    title: safeString(data.title, 'Untitled'),
    tags: safeStringArray(data.tags),
    project: safeString(data.project, 'default'),
    format: safeFormat(data.format),
    created: safeISODate(data.created),
    updated: safeISODate(data.updated),
    content: body.trim(),
  };
}

// Serialize Note to file content
function serializeNote(note: Note): string {
  const frontmatter: NoteMeta = {
    id: note.id,
    type: note.type,
    title: note.title,
    tags: note.tags,
    project: note.project,
    format: note.format,
    created: note.created,
    updated: note.updated,
  };

  return matter.stringify(note.content, frontmatter);
}

// Convert Note to IndexEntry
function noteToIndexEntry(note: Note): IndexEntry {
  return {
    id: note.id,
    type: note.type,
    title: note.title,
    tags: note.tags,
    project: note.project,
    created: note.created,
    updated: note.updated,
  };
}

// Create a new note
export async function createNote(input: CreateNoteInput): Promise<Note> {
  const config = await readConfig();
  const id = generateNoteId();
  const now = new Date().toISOString();

  const note: Note = {
    id,
    type: input.type,
    title: input.title,
    content: input.content,
    tags: input.tags || [],
    project: input.project || config.defaultProject,
    format: input.format || config.defaultFormat,
    created: now,
    updated: now,
  };

  // Ensure project directory exists
  await ensureProjectDir(note.project);

  // Write note file
  const filePath = getNotePath(note.project, note.id);
  await writeFileContent(filePath, serializeNote(note));

  // Update index
  const index = await readIndex();
  index.entries.push(noteToIndexEntry(note));
  await writeIndex(index);

  return note;
}

// Read a note by ID
export async function readNote(id: string): Promise<Note | null> {
  const index = await readIndex();
  const entry = index.entries.find(e => e.id === id);

  if (!entry) {
    return null;
  }

  const filePath = getNotePath(entry.project, id);
  const content = await readFileContent(filePath);

  if (!content) {
    return null;
  }

  return parseNoteFile(content, id);
}

// Update an existing note
export async function updateNote(id: string, input: UpdateNoteInput): Promise<Note | null> {
  const existingNote = await readNote(id);

  if (!existingNote) {
    return null;
  }

  const updatedNote: Note = {
    ...existingNote,
    ...input,
    updated: new Date().toISOString(),
  };

  // Handle project change
  if (input.project && input.project !== existingNote.project) {
    // Delete old file
    const oldPath = getNotePath(existingNote.project, id);
    await deleteFile(oldPath);

    // Create in new project
    await ensureProjectDir(input.project);
  }

  // Write updated note
  const filePath = getNotePath(updatedNote.project, id);
  await writeFileContent(filePath, serializeNote(updatedNote));

  // Update index
  const index = await readIndex();
  const entryIndex = index.entries.findIndex(e => e.id === id);
  if (entryIndex >= 0) {
    index.entries[entryIndex] = noteToIndexEntry(updatedNote);
    await writeIndex(index);
  }

  return updatedNote;
}

// Delete a note
export async function deleteNote(id: string): Promise<boolean> {
  const index = await readIndex();
  const entry = index.entries.find(e => e.id === id);

  if (!entry) {
    return false;
  }

  // Delete file
  const filePath = getNotePath(entry.project, id);
  const deleted = await deleteFile(filePath);

  if (!deleted) {
    return false;
  }

  // Update index
  index.entries = index.entries.filter(e => e.id !== id);
  await writeIndex(index);

  return true;
}

// List notes with optional filtering (optimized single-pass)
export async function listNotes(filter?: NoteFilter): Promise<IndexEntry[]> {
  const index = await readIndex();

  // No filter: return all entries sorted
  if (!filter) {
    return index.entries.sort((a, b) =>
      new Date(b.updated).getTime() - new Date(a.updated).getTime()
    );
  }

  // Pre-compute search term for efficiency
  const searchLower = filter.search?.toLowerCase();
  const filterTags = filter.tags && filter.tags.length > 0 ? filter.tags : null;

  // Single-pass filtering
  const filtered = index.entries.filter(entry => {
    // Type filter
    if (filter.type && entry.type !== filter.type) return false;

    // Project filter
    if (filter.project && entry.project !== filter.project) return false;

    // Tags filter (any match)
    if (filterTags && !filterTags.some(tag => entry.tags.includes(tag))) return false;

    // Search filter (title or tags)
    if (searchLower) {
      const titleMatch = entry.title.toLowerCase().includes(searchLower);
      const tagMatch = entry.tags.some(tag => tag.toLowerCase().includes(searchLower));
      if (!titleMatch && !tagMatch) return false;
    }

    return true;
  });

  // Sort by updated date, newest first
  return filtered.sort((a, b) =>
    new Date(b.updated).getTime() - new Date(a.updated).getTime()
  );
}

// Get note by ID (returns full note)
export async function getNote(id: string): Promise<Note | null> {
  return readNote(id);
}

// Check if note exists
export async function noteExists(id: string): Promise<boolean> {
  const index = await readIndex();
  return index.entries.some(e => e.id === id);
}

// Get all unique tags
export async function getAllTags(): Promise<string[]> {
  const index = await readIndex();
  const tagSet = new Set<string>();

  for (const entry of index.entries) {
    for (const tag of entry.tags) {
      tagSet.add(tag);
    }
  }

  return Array.from(tagSet).sort();
}

// Get all projects
export async function getAllProjects(): Promise<string[]> {
  return await listProjectDirs();
}

// Rebuild index from files (parallelized I/O)
export async function rebuildIndex(): Promise<number> {
  const projects = await listProjectDirs();

  // Gather all note file info in parallel per project
  const projectNotes = await Promise.all(
    projects.map(async (project) => {
      const noteIds = await listNoteFiles(project);
      return noteIds.map(id => ({ project, id }));
    })
  );

  // Flatten to single array of {project, id}
  const allNotes = projectNotes.flat();

  // Read all note files in parallel (with concurrency limit)
  const BATCH_SIZE = 50;
  const entries: IndexEntry[] = [];

  for (let i = 0; i < allNotes.length; i += BATCH_SIZE) {
    const batch = allNotes.slice(i, i + BATCH_SIZE);
    const results = await Promise.all(
      batch.map(async ({ project, id }) => {
        const filePath = getNotePath(project, id);
        const content = await readFileContent(filePath);
        if (content) {
          const note = parseNoteFile(content, id);
          return noteToIndexEntry(note);
        }
        return null;
      })
    );
    entries.push(...results.filter((e): e is IndexEntry => e !== null));
  }

  const index = {
    version: '1.0',
    lastUpdated: new Date().toISOString(),
    entries,
  };

  await writeIndex(index);
  return entries.length;
}
