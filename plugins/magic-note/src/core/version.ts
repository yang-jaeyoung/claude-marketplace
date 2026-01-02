/**
 * Version management - single source of truth from package.json
 */

// Import version from package.json at build time
import pkg from '../../package.json';

export const VERSION = pkg.version;
export const NAME = pkg.name;
export const DESCRIPTION = pkg.description;
