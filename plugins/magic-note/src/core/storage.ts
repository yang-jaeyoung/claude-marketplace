/**
 * Storage layer for file I/O operations
 * Uses Bun's native file APIs for better performance
 */

import { mkdir, readdir, unlink } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';
import type { StoragePaths, NoteIndex, AppConfig } from './types';
import { VERSION } from './version';

// Default storage root
const STORAGE_ROOT = join(homedir(), '.magic-note');

// Get all storage paths
export function getStoragePaths(): StoragePaths {
  return {
    root: STORAGE_ROOT,
    projects: join(STORAGE_ROOT, 'projects'),
    templates: join(STORAGE_ROOT, 'templates'),
    config: join(STORAGE_ROOT, 'config.yaml'),
    index: join(STORAGE_ROOT, 'index.json'),
  };
}

// Check if storage is initialized
export async function isInitialized(): Promise<boolean> {
  const paths = getStoragePaths();
  return await Bun.file(paths.root).exists();
}

// Initialize storage directories
export async function initStorage(): Promise<void> {
  const paths = getStoragePaths();

  await mkdir(paths.root, { recursive: true });
  await mkdir(paths.projects, { recursive: true });
  await mkdir(paths.templates, { recursive: true });

  // Create default config if not exists
  if (!(await Bun.file(paths.config).exists())) {
    await writeDefaultConfig();
  }

  // Create empty index if not exists
  if (!(await Bun.file(paths.index).exists())) {
    await writeIndex(createEmptyIndex());
  }
}

// Default configuration
export function getDefaultConfig(): AppConfig {
  return {
    version: VERSION,
    defaultProject: 'default',
    defaultEditor: process.env.EDITOR || 'vim',
    defaultFormat: 'markdown',
    dateFormat: 'YYYY-MM-DD HH:mm:ss',
  };
}

// Write default config
async function writeDefaultConfig(): Promise<void> {
  const paths = getStoragePaths();
  const { stringify } = await import('yaml');
  const config = getDefaultConfig();
  await Bun.write(paths.config, stringify(config));
}

// Create empty index
function createEmptyIndex(): NoteIndex {
  return {
    version: '1.0',
    lastUpdated: new Date().toISOString(),
    entries: [],
  };
}

// Read index with error recovery
export async function readIndex(): Promise<NoteIndex> {
  const paths = getStoragePaths();
  const file = Bun.file(paths.index);

  if (!(await file.exists())) {
    return createEmptyIndex();
  }

  try {
    const content = await file.text();
    const parsed = JSON.parse(content);

    // Validate basic structure
    if (!parsed || typeof parsed !== 'object' || !Array.isArray(parsed.entries)) {
      console.error('Invalid index structure, resetting to empty index');
      return createEmptyIndex();
    }

    return parsed as NoteIndex;
  } catch (error) {
    console.error('Failed to parse index.json, resetting to empty index:', error);
    return createEmptyIndex();
  }
}

// Write index
export async function writeIndex(index: NoteIndex): Promise<void> {
  const paths = getStoragePaths();
  index.lastUpdated = new Date().toISOString();
  await Bun.write(paths.index, JSON.stringify(index, null, 2));
}

// Get project directory path
export function getProjectPath(projectName: string): string {
  const paths = getStoragePaths();
  return join(paths.projects, projectName);
}

// Get note file path
export function getNotePath(projectName: string, noteId: string): string {
  return join(getProjectPath(projectName), `${noteId}.md`);
}

// Get template file path
export function getTemplatePath(templateName: string): string {
  const paths = getStoragePaths();
  return join(paths.templates, `${templateName}.md`);
}

// Ensure project directory exists
export async function ensureProjectDir(projectName: string): Promise<void> {
  const projectPath = getProjectPath(projectName);
  await mkdir(projectPath, { recursive: true });
}

// List all project directories
export async function listProjectDirs(): Promise<string[]> {
  const paths = getStoragePaths();

  if (!(await Bun.file(paths.projects).exists())) {
    return [];
  }

  const entries = await readdir(paths.projects, { withFileTypes: true });
  return entries
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name);
}

// List all note files in a project
export async function listNoteFiles(projectName: string): Promise<string[]> {
  const projectPath = getProjectPath(projectName);

  if (!(await Bun.file(projectPath).exists())) {
    return [];
  }

  const entries = await readdir(projectPath, { withFileTypes: true });
  return entries
    .filter(entry => entry.isFile() && entry.name.endsWith('.md'))
    .map(entry => entry.name.replace('.md', ''));
}

// List all template files
export async function listTemplateFiles(): Promise<string[]> {
  const paths = getStoragePaths();

  if (!(await Bun.file(paths.templates).exists())) {
    return [];
  }

  const entries = await readdir(paths.templates, { withFileTypes: true });
  return entries
    .filter(entry => entry.isFile() && entry.name.endsWith('.md'))
    .map(entry => entry.name.replace('.md', ''));
}

// Read file content using Bun.file
export async function readFileContent(filePath: string): Promise<string | null> {
  const file = Bun.file(filePath);
  if (!(await file.exists())) {
    return null;
  }
  return await file.text();
}

// Write file content using Bun.write
export async function writeFileContent(filePath: string, content: string): Promise<void> {
  await Bun.write(filePath, content);
}

// Delete file
export async function deleteFile(filePath: string): Promise<boolean> {
  const file = Bun.file(filePath);
  if (!(await file.exists())) {
    return false;
  }
  await unlink(filePath);
  return true;
}

// Check if file exists using Bun.file
export async function fileExists(filePath: string): Promise<boolean> {
  return await Bun.file(filePath).exists();
}
