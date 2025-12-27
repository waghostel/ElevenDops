# Naming Conventions

This document defines the naming conventions that MUST be followed throughout the project.

---

## File Naming

### General Rules

- Use **kebab-case** for all file names
- Use **double hyphens (`--`)** to separate semantic parts
- Use only lowercase letters and numbers
- Never use spaces, underscores, or camelCase

### Examples

| ✅ Correct                   | ❌ Incorrect                |
| :--------------------------- | :-------------------------- |
| `user-profile--settings.tsx` | `UserProfileSettings.tsx`   |
| `api-spec--order-service.md` | `api_spec_order_service.md` |
| `guide--getting-started.md`  | `guide getting started.md`  |

---

## Directory Naming

- Use **kebab-case** for directory names
- Keep names short but descriptive
- Avoid abbreviations unless universally understood

### Examples

| ✅ Correct         | ❌ Incorrect      |
| :----------------- | :---------------- |
| `user-management/` | `userManagement/` |
| `api-routes/`      | `API_Routes/`     |
| `auth-utils/`      | `authUtils/`      |

---

## Code Naming

### TypeScript/JavaScript

| Element      | Convention                            | Example                           |
| :----------- | :------------------------------------ | :-------------------------------- |
| Variables    | camelCase                             | `userName`, `isLoading`           |
| Constants    | SCREAMING_SNAKE_CASE                  | `MAX_RETRIES`, `API_URL`          |
| Functions    | camelCase                             | `getUserById()`, `handleSubmit()` |
| Classes      | PascalCase                            | `UserService`, `AuthController`   |
| Interfaces   | PascalCase with `I` prefix (optional) | `IUserData` or `UserData`         |
| Types        | PascalCase                            | `UserRole`, `ApiResponse`         |
| Enums        | PascalCase                            | `UserStatus`, `HttpMethod`        |
| Enum Members | SCREAMING_SNAKE_CASE                  | `ACTIVE`, `PENDING_APPROVAL`      |

### Python

| Element   | Convention           | Example                               |
| :-------- | :------------------- | :------------------------------------ |
| Variables | snake_case           | `user_name`, `is_loading`             |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `API_URL`              |
| Functions | snake_case           | `get_user_by_id()`, `handle_submit()` |
| Classes   | PascalCase           | `UserService`, `AuthController`       |
| Module    | snake_case           | `user_service.py`, `auth_utils.py`    |

---

## Component Naming (React)

- Component files: PascalCase (e.g., `UserProfile.tsx`)
- Component folders: PascalCase (e.g., `UserProfile/`)
- Style files: Same as component with `.module.css` suffix

### Structure Example

```
components/
└── UserProfile/
    ├── UserProfile.tsx
    ├── UserProfile.module.css
    ├── UserProfile.test.tsx
    └── index.ts
```

---

## Test File Naming

| Test Type   | Pattern                 | Example                        |
| :---------- | :---------------------- | :----------------------------- |
| Unit Test   | `*.test.ts`             | `user-service.test.ts`         |
| Integration | `*.integration.test.ts` | `auth-api.integration.test.ts` |
| E2E         | `*.e2e.ts`              | `login-flow.e2e.ts`            |

---

## API Naming

### Endpoints

- Use **kebab-case** for URL paths
- Use **plural nouns** for resources
- Use HTTP methods for actions

| ✅ Correct            | ❌ Incorrect               |
| :-------------------- | :------------------------- |
| `GET /users`          | `GET /getUsers`            |
| `POST /user-profiles` | `POST /userProfiles`       |
| `DELETE /orders/{id}` | `DELETE /deleteOrder/{id}` |

### Query Parameters

- Use **camelCase** for query parameters

```
GET /users?sortBy=createdAt&pageSize=10
```
