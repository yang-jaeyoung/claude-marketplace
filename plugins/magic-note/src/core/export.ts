/**
 * Export and Import functionality
 */

import { stringify as yamlStringify, parse as yamlParse } from 'yaml';
import type {
  Note,
  ExportFormat,
  ExportOptions,
  ImportResult,
  NoteFilter,
  CreateNoteInput,
  NoteType,
  ContentFormat,
} from './types';
import { listNotes, getNote, createNote } from './note';

// Export data structure
interface ExportData {
  version: string;
  exportedAt: string;
  notes: Note[];
}

// Valid values for validation
const VALID_NOTE_TYPES: readonly string[] = ['prompt', 'plan', 'choice'];
const VALID_FORMATS: readonly string[] = ['markdown', 'text', 'xml', 'yaml'];

// Validate imported note structure
function validateImportedNote(note: unknown, index: number): { valid: boolean; error?: string; note?: CreateNoteInput } {
  if (!note || typeof note !== 'object') {
    return { valid: false, error: `Note at index ${index}: invalid structure` };
  }

  const n = note as Record<string, unknown>;

  // Validate required fields
  if (typeof n.type !== 'string' || !VALID_NOTE_TYPES.includes(n.type)) {
    return { valid: false, error: `Note at index ${index}: invalid or missing type` };
  }

  if (typeof n.title !== 'string' || n.title.length === 0 || n.title.length > 500) {
    return { valid: false, error: `Note at index ${index}: invalid or missing title` };
  }

  if (typeof n.content !== 'string') {
    return { valid: false, error: `Note at index ${index}: invalid or missing content` };
  }

  // Validate optional fields
  let tags: string[] = [];
  if (n.tags !== undefined) {
    if (!Array.isArray(n.tags)) {
      return { valid: false, error: `Note at index ${index}: tags must be an array` };
    }
    tags = n.tags.filter((t): t is string => typeof t === 'string' && t.length <= 100).slice(0, 50);
  }

  let project: string | undefined;
  if (n.project !== undefined) {
    if (typeof n.project !== 'string' || n.project.length > 100) {
      return { valid: false, error: `Note at index ${index}: invalid project` };
    }
    project = n.project;
  }

  let format: ContentFormat | undefined;
  if (n.format !== undefined) {
    if (typeof n.format !== 'string' || !VALID_FORMATS.includes(n.format)) {
      return { valid: false, error: `Note at index ${index}: invalid format` };
    }
    format = n.format as ContentFormat;
  }

  return {
    valid: true,
    note: {
      type: n.type as NoteType,
      title: n.title,
      content: n.content.slice(0, 100000), // Limit content size
      tags,
      project,
      format,
    },
  };
}

// Export notes (parallelized note loading)
export async function exportNotes(options: ExportOptions): Promise<string> {
  // Build filter
  const filter: NoteFilter = {};
  if (options.project) filter.project = options.project;
  if (options.tags) filter.tags = options.tags;
  if (options.type) filter.type = options.type;

  // Get note entries
  const entries = await listNotes(filter);

  // Load all notes in parallel
  const results = await Promise.all(
    entries.map(entry => getNote(entry.id))
  );
  const notes = results.filter((n): n is Note => n !== null);

  const exportData: ExportData = {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    notes,
  };

  // Format output
  switch (options.format) {
    case 'yaml':
      return yamlStringify(exportData);

    case 'markdown':
      return exportToMarkdown(notes);

    case 'json':
    default:
      return JSON.stringify(exportData, null, 2);
  }
}

// Export to markdown format
function exportToMarkdown(notes: Note[]): string {
  const lines: string[] = [
    '# Magic Note Export',
    '',
    `Exported at: ${new Date().toLocaleString()}`,
    `Total notes: ${notes.length}`,
    '',
    '---',
    '',
  ];

  for (const note of notes) {
    lines.push(`## ${note.title}`);
    lines.push('');
    lines.push(`- **ID**: ${note.id}`);
    lines.push(`- **Type**: ${note.type}`);
    lines.push(`- **Project**: ${note.project}`);
    lines.push(`- **Tags**: ${note.tags.join(', ') || 'None'}`);
    lines.push(`- **Created**: ${new Date(note.created).toLocaleString()}`);
    lines.push('');
    lines.push('### Content');
    lines.push('');
    lines.push(note.content);
    lines.push('');
    lines.push('---');
    lines.push('');
  }

  return lines.join('\n');
}

// Save export to file using Bun.write
export async function saveExport(
  content: string,
  outputPath: string
): Promise<void> {
  await Bun.write(outputPath, content);
}

// Validate export data structure
function validateExportData(data: unknown): { valid: boolean; error?: string; notes?: unknown[] } {
  if (!data || typeof data !== 'object') {
    return { valid: false, error: 'Invalid export data: not an object' };
  }

  const d = data as Record<string, unknown>;

  if (!Array.isArray(d.notes)) {
    return { valid: false, error: 'Invalid export format: missing notes array' };
  }

  if (d.notes.length > 10000) {
    return { valid: false, error: 'Too many notes in export file (max 10000)' };
  }

  return { valid: true, notes: d.notes };
}

// Import notes from file with validation (using Bun.file)
export async function importNotes(filePath: string): Promise<ImportResult> {
  const result: ImportResult = {
    success: 0,
    failed: 0,
    errors: [],
  };

  try {
    const file = Bun.file(filePath);

    // Check if file exists
    if (!(await file.exists())) {
      result.errors.push(`Import failed: file not found: ${filePath}`);
      return result;
    }

    // Check file size before reading (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      result.errors.push('Import failed: file too large (max 10MB)');
      return result;
    }

    const content = await file.text();

    // Double-check content length
    if (content.length > 10 * 1024 * 1024) {
      result.errors.push('Import failed: file too large (max 10MB)');
      return result;
    }

    let data: unknown;

    // Try to parse as JSON first, then YAML
    try {
      data = JSON.parse(content);
    } catch {
      try {
        data = yamlParse(content);
      } catch (yamlErr) {
        result.errors.push(`Import failed: invalid JSON/YAML format`);
        return result;
      }
    }

    // Validate export structure
    const exportValidation = validateExportData(data);
    if (!exportValidation.valid) {
      result.errors.push(`Import failed: ${exportValidation.error}`);
      return result;
    }

    // Process each note with validation
    for (let i = 0; i < exportValidation.notes!.length; i++) {
      const noteData = exportValidation.notes![i];
      const validation = validateImportedNote(noteData, i);

      if (!validation.valid) {
        result.failed++;
        result.errors.push(validation.error!);
        continue;
      }

      try {
        await createNote(validation.note!);
        result.success++;
      } catch (err) {
        result.failed++;
        result.errors.push(`Failed to create note at index ${i}: ${(err as Error).message}`);
      }
    }
  } catch (err) {
    result.errors.push(`Import failed: ${(err as Error).message}`);
  }

  return result;
}
