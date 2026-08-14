## Why

The platform needs a defined, tested path for a Django user to sign in to the
administration site and review the posts stored in the database. The existing
`Post` registration does not document or verify this end-to-end behavior.

## What Changes

- Define authenticated access to the Django administration site for staff users.
- Define how registered `Post` records are presented in the administration list.
- Add automated coverage for admin authentication and post-list visibility.

## Capabilities

### New Capabilities
- `django-admin-post-access`: Authenticated staff access to the Django admin and
  visibility of persisted posts.

### Modified Capabilities

- None.

## Impact

- `project/posts/admin.py` and its tests.
- Django's built-in authentication and admin URLs.
