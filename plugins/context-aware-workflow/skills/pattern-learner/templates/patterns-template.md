# Patterns Template

Use this template for documenting learned project patterns.

---

```markdown
# Project Patterns

## Metadata

| Field | Value |
|-------|-------|
| **Analyzed** | YYYY-MM-DD HH:MM |
| **Files Scanned** | N files |
| **Language** | TypeScript / Python / Go / Mixed |
| **Framework** | React / FastAPI / Express / None |
| **Package Manager** | npm / yarn / pnpm / pip / go mod |

---

## Code Style Patterns

### Naming Conventions

| Element | Pattern | Confidence | Example |
|---------|---------|------------|---------|
| Functions | camelCase | High | `getUserById()` |
| Classes | PascalCase | High | `UserService` |
| Interfaces | I-prefix | Medium | `IUserRepository` |
| Types | T-prefix or PascalCase | Medium | `TUserData` or `UserData` |
| Constants | UPPER_SNAKE_CASE | High | `MAX_RETRY_COUNT` |
| Enums | PascalCase | High | `UserStatus` |
| Files (components) | PascalCase | High | `UserProfile.tsx` |
| Files (utilities) | kebab-case | High | `format-date.ts` |
| Directories | kebab-case | High | `user-management/` |

### Import Organization

```typescript
// 1. External packages (alphabetical)
import express from 'express';
import { z } from 'zod';

// 2. Internal aliases (alphabetical)
import { User } from '@/models';
import { logger } from '@/utils';

// 3. Relative imports (parent first, then siblings)
import { BaseService } from '../base';
import { validate } from './validators';

// 4. Type imports (if separated)
import type { UserDTO } from '@/types';
```

### Code Formatting

| Aspect | Pattern |
|--------|---------|
| Indentation | 2 spaces / 4 spaces / tabs |
| Quotes | Single / Double |
| Semicolons | Required / Omitted |
| Trailing Commas | ES5 / All / None |
| Line Length | 80 / 100 / 120 |
| Bracket Spacing | `{ foo }` / `{foo}` |

---

## Architecture Patterns

### Directory Structure

```
src/
├── components/          # UI Components
│   ├── common/          # Shared components
│   └── features/        # Feature-specific
├── services/            # Business logic
├── repositories/        # Data access layer
├── models/              # Data structures
├── utils/               # Utility functions
├── hooks/               # React hooks (if applicable)
├── types/               # Type definitions
└── constants/           # Constants and configs
```

### Module Pattern

| Pattern | Description |
|---------|-------------|
| Barrel Exports | Use `index.ts` for directory exports |
| Single Export | One main export per file |
| Named Exports | Prefer named over default exports |

### Dependency Direction

```
Controllers → Services → Repositories → Models
     ↓            ↓           ↓
  Validators   Utils     Database
```

---

## Error Handling Patterns

### Pattern Type

[Select one or describe custom pattern]

**Option A: Try-Catch**
```typescript
try {
  const result = await operation();
  return result;
} catch (error) {
  logger.error('Operation failed', { error });
  throw new ServiceError('Operation failed', error);
}
```

**Option B: Result Type**
```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function getUser(id: string): Result<User> {
  // Returns Result instead of throwing
}
```

**Option C: Error Classes**
```typescript
class NotFoundError extends BaseError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`);
  }
}
```

### Error Logging

| Aspect | Pattern |
|--------|---------|
| Logger | winston / pino / console |
| Format | Structured JSON / Plain text |
| Levels | error, warn, info, debug |
| Context | Include request ID, user ID |

---

## Testing Patterns

### Test Location

| Pattern | Structure |
|---------|-----------|
| Co-located | `src/user/user.service.ts` → `src/user/user.service.test.ts` |
| Separate | `src/user/service.ts` → `tests/user/service.test.ts` |
| __tests__ | `src/user/service.ts` → `src/user/__tests__/service.test.ts` |

### Test Naming

```typescript
// File: user.service.test.ts

describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', () => {});
    it('should throw error when email is invalid', () => {});
    it('should hash password before saving', () => {});
  });
});
```

### Test Structure (AAA Pattern)

```typescript
it('should create user with valid data', () => {
  // Arrange
  const userData = { name: 'Test', email: 'test@example.com' };
  const mockRepo = { save: jest.fn().mockResolvedValue({ id: '1' }) };

  // Act
  const result = await service.createUser(userData);

  // Assert
  expect(result.id).toBe('1');
  expect(mockRepo.save).toHaveBeenCalledWith(userData);
});
```

### Mocking Approach

| Approach | When to Use |
|----------|-------------|
| jest.mock() | External modules |
| Dependency Injection | Services, repositories |
| Manual mocks | Complex behaviors |
| jest.spyOn() | Partial mocking |

---

## API Patterns (if applicable)

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "total": 100
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": { ... }
  }
}
```

### Endpoint Naming

| Pattern | Example |
|---------|---------|
| Resource-based | `GET /users`, `POST /users` |
| Action suffix | `POST /users/123/activate` |
| Nested resources | `GET /users/123/orders` |

---

## Documentation Patterns

### Code Comments

```typescript
/**
 * Retrieves a user by their unique identifier.
 *
 * @param id - The user's unique identifier
 * @returns The user object if found
 * @throws {NotFoundError} When user doesn't exist
 *
 * @example
 * const user = await getUserById('123');
 */
async function getUserById(id: string): Promise<User> {
  // Implementation
}
```

### README Structure

1. Title and description
2. Installation instructions
3. Usage examples
4. Configuration
5. API documentation
6. Contributing guidelines

---

## Confidence Summary

| Category | Confidence | Notes |
|----------|------------|-------|
| Naming | High | Consistent across codebase |
| Architecture | High | Clear structure |
| Error Handling | Medium | Some inconsistencies |
| Testing | Medium | Coverage varies |
| Documentation | Low | Needs improvement |
```

---

## Template Usage Notes

1. **Fill only observed patterns** - Leave sections empty if no clear pattern
2. **Include confidence** - Helps prioritize enforcement
3. **Provide examples** - Real code examples from the project
4. **Note exceptions** - Document intentional deviations
5. **Update regularly** - Refresh when codebase evolves
