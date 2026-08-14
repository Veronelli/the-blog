## Context

The `Post` model is already registered in Django administration with title and
creation timestamp columns. The change needs to make the built-in staff-only
access and post-list behavior explicit and covered by tests.

## Goals / Non-Goals

**Goals:**
- Verify staff authentication, unauthenticated redirects, and post-list content.
- Keep the existing Django administration URL and authentication flow.

**Non-Goals:**
- Add public post browsing, custom login pages, or new authorization roles.
- Change the `Post` database schema or create users automatically.

## Decisions

- Use Django's built-in administration authentication and staff permission
  checks rather than custom middleware. This preserves framework security
  defaults; custom access control would duplicate established behavior.
- Exercise the post changelist through Django's test client with a staff user
  and persisted `Post` instance. This verifies the user-visible integration
  rather than only the model registration.

## Risks / Trade-offs

- [Administration requires a staff account] -> Document and test the staff-user
  prerequisite; provisioning remains an operational Django task.
- [Tests depend on Django administration routes] -> Use Django's named admin
  URLs so route changes are detected by the test suite.

## Migration Plan

No data migration is required. Deploy the code and run the Django test suite;
rollback consists of reverting the code-only change.
