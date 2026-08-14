## 1. Administration Behavior

- [ ] 1.1 Confirm the `Post` administration registration exposes the title and creation timestamp in its list view.
- [ ] 1.2 Preserve Django's staff-only administration access for the post list.

## 2. Automated Coverage

- [ ] 2.1 Add a test that redirects an unauthenticated request for the post administration list to the login page.
- [ ] 2.2 Add a test that authenticates a staff user and verifies the post administration list displays persisted post details.

## 3. Verification

- [ ] 3.1 Run the posts test suite and Django system checks.
