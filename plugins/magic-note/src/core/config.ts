/**
 * Configuration management
 */

import { parse, stringify } from 'yaml';
import type { AppConfig } from './types';
import {
  getStoragePaths,
  getDefaultConfig,
  readFileContent,
  writeFileContent,
  fileExists,
} from './storage';

// Read configuration
export async function readConfig(): Promise<AppConfig> {
  const paths = getStoragePaths();

  const content = await readFileContent(paths.config);
  if (!content) {
    return getDefaultConfig();
  }

  const parsed = parse(content) as Partial<AppConfig>;
  return {
    ...getDefaultConfig(),
    ...parsed,
  };
}

// Write configuration
export async function writeConfig(config: AppConfig): Promise<void> {
  const paths = getStoragePaths();
  await writeFileContent(paths.config, stringify(config));
}

// Update configuration partially
export async function updateConfig(updates: Partial<AppConfig>): Promise<AppConfig> {
  const current = await readConfig();
  const updated = { ...current, ...updates };
  await writeConfig(updated);
  return updated;
}

// Get specific config value
export async function getConfigValue<K extends keyof AppConfig>(
  key: K
): Promise<AppConfig[K]> {
  const config = await readConfig();
  return config[key];
}

// Set specific config value
export async function setConfigValue<K extends keyof AppConfig>(
  key: K,
  value: AppConfig[K]
): Promise<void> {
  const config = await readConfig();
  config[key] = value;
  await writeConfig(config);
}

// Check if config exists
export async function configExists(): Promise<boolean> {
  const paths = getStoragePaths();
  return await fileExists(paths.config);
}

// Reset config to defaults
export async function resetConfig(): Promise<AppConfig> {
  const defaultConfig = getDefaultConfig();
  await writeConfig(defaultConfig);
  return defaultConfig;
}
