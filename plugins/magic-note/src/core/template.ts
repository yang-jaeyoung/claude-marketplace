/**
 * Template management
 */

import matter from 'gray-matter';
import type { Template, CreateTemplateInput, NoteType } from './types';
import {
  getTemplatePath,
  readFileContent,
  writeFileContent,
  deleteFile,
  fileExists,
  listTemplateFiles,
  getStoragePaths,
} from './storage';
import { mkdir } from 'fs/promises';

// Parse template file
function parseTemplateFile(content: string, name: string): Template {
  const { data, content: body } = matter(content);

  return {
    name,
    type: data.type || 'prompt',
    tags: data.tags || [],
    content: body.trim(),
    description: data.description || '',
    created: data.created || new Date().toISOString(),
  };
}

// Serialize template to file content
function serializeTemplate(template: Template): string {
  const frontmatter = {
    type: template.type,
    tags: template.tags,
    description: template.description,
    created: template.created,
  };

  return matter.stringify(template.content, frontmatter);
}

// Create a new template
export async function createTemplate(input: CreateTemplateInput): Promise<Template> {
  const paths = getStoragePaths();
  await mkdir(paths.templates, { recursive: true });

  const template: Template = {
    name: input.name,
    type: input.type,
    tags: input.tags || [],
    content: input.content,
    description: input.description || '',
    created: new Date().toISOString(),
  };

  const filePath = getTemplatePath(input.name);
  await writeFileContent(filePath, serializeTemplate(template));

  return template;
}

// Get a template by name
export async function getTemplate(name: string): Promise<Template | null> {
  const filePath = getTemplatePath(name);
  const content = await readFileContent(filePath);

  if (!content) {
    return null;
  }

  return parseTemplateFile(content, name);
}

// List all templates (parallelized I/O)
export async function listTemplates(): Promise<Template[]> {
  const templateNames = await listTemplateFiles();

  // Read all templates in parallel
  const results = await Promise.all(
    templateNames.map(name => getTemplate(name))
  );

  // Filter out nulls
  return results.filter((t): t is Template => t !== null);
}

// Delete a template
export async function deleteTemplate(name: string): Promise<boolean> {
  const filePath = getTemplatePath(name);
  return await deleteFile(filePath);
}

// Check if template exists
export async function templateExists(name: string): Promise<boolean> {
  const filePath = getTemplatePath(name);
  return await fileExists(filePath);
}

// Escape special regex characters to prevent ReDoS attacks
function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Validate variable key (alphanumeric and underscore only)
function isValidVariableKey(key: string): boolean {
  return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(key) && key.length <= 50;
}

// Apply template variables (safe placeholder replacement)
export function applyTemplateVariables(
  content: string,
  variables: Record<string, string>
): string {
  let result = content;

  for (const [key, value] of Object.entries(variables)) {
    // Skip invalid keys to prevent injection
    if (!isValidVariableKey(key)) {
      console.warn(`Skipping invalid template variable key: ${key}`);
      continue;
    }

    // Sanitize value length
    const safeValue = typeof value === 'string' ? value.slice(0, 10000) : '';

    // Use escaped key in regex for safety
    const placeholder = new RegExp(`\\{\\{\\s*${escapeRegExp(key)}\\s*\\}\\}`, 'g');
    result = result.replace(placeholder, safeValue);
  }

  return result;
}
