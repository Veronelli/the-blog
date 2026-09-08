## 1. Post Identifier And Persistence

- [ ] 1.1 Add model tests for title normalization, URL-safe `unique_name`, recalculation after title changes, same-author collisions, and equal slugs across different authors; verify the tests fail before implementation.
- [ ] 1.2 Add the persisted `unique_name` field, deterministic title normalization, and model validation/save behavior; verify the model tests pass.
- [ ] 1.3 Add the database uniqueness constraint for `(author, unique_name)` and a data migration for existing posts; verify migration tests and the duplicate constraint behavior pass.
- [ ] 1.4 Resolve or explicitly fail pre-existing normalized title collisions during migration without silently suffixing identifiers; verify the migration reports the conflicting author and titles.

## 2. Public Post API Contract

- [ ] 2.1 Add serializer tests asserting the exact public response fields and exclusion of user/account and unrelated relationship data; verify the serializer tests pass.
- [ ] 2.2 Implement the explicit read serializer for `unique_name`, title, content, timestamps, and author `public_username`; verify collection and detail serialization use the same shape.
- [ ] 2.3 Add endpoint tests for anonymous collection and detail GET requests, missing profiles/posts, cross-author slug mismatches, and unsupported write methods; verify expected HTTP statuses and unchanged data.
- [ ] 2.4 Implement public read-only views scoped first by `public_username` and then by `unique_name`; verify endpoint tests pass and no global ID lookup is used.

## 3. Routing And Integration

- [ ] 3.1 Add routing tests for `/api/authors/<public_username>/posts/` and `/api/authors/<public_username>/posts/<unique_name>/`, including trailing-slash behavior; verify both routes resolve to the intended views.
- [ ] 3.2 Register the nested post routes alongside the existing public author routes while keeping development-only login and schema routes environment-gated; verify routing tests pass in development and production-style settings.
- [ ] 3.3 Run `uv run python project/manage.py check` and the relevant posts/API test directories; verify no configuration, import, migration, or routing errors remain.
- [ ] 3.4 Run `uv run pytest` for the complete suite and verify all existing author endpoint behavior remains passing.
