/**
 * Core type definitions for Magic Note
 */

// Note types
export type NoteType = 'prompt' | 'plan' | 'choice' | 'insight';

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
}
