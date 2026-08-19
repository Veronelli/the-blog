## 1. Foundation

- [ ] 1.1 Create the `profiles` Django application and register it in project settings.
- [ ] 1.2 Create test fixtures and factories for users, variables, social network configurations, instances, and public profiles.

## 2. Reusable variables and instances

- [ ] 2.1 [RED] Add failing model tests for variable labels, descriptions, regular-expression validation, parent social-network-instance ownership, and archiving.
- [ ] 2.2 [GREEN] Implement variables and variable instances with model-level validation, parent-derived ownership, and archival behavior.
- [ ] 2.3 [REFACTOR] Simplify variable validation, parent-derived ownership, and archival handling while preserving the passing model tests.
- [ ] 2.4 [RED] Add failing admin permission and validation tests for variables.
- [ ] 2.5 [GREEN] Register variables in Django admin with staff-only management.

## 3. Social network configurations and instances

- [ ] 3.1 [RED] Add failing model tests for social network configurations, `template_url`, `icon_url`, associated variables, permitted variable instances, immutable authors, archival, and URL construction.
- [ ] 3.2 [GREEN] Implement social network configurations and user social network instances with validation, immutable author, and archival behavior.
- [ ] 3.3 [REFACTOR] Simplify configuration, ownership, archival, and URL-building interfaces while preserving the passing model tests.
- [ ] 3.4 [RED] Add failing admin permission and validation tests for social network configurations.
- [ ] 3.5 [GREEN] Register social network configurations in Django admin with staff-only management.

## 4. Public profile identity

- [ ] 4.1 [RED] Add failing model and form tests for public-profile fields, unique `public_username`, optional valid `photo_url`, and validation errors.
- [ ] 4.2 [GREEN] Implement the public profile model and dashboard form using `public_username` as the public identifier and `photo_url` as an external image URL.
- [ ] 4.3 [REFACTOR] Simplify profile validation and form handling while preserving the passing tests.
- [ ] 4.4 Generate and apply the initial migrations for the profiles application.

## 5. User social network dashboard

- [ ] 5.1 [RED] Add failing dashboard tests for ownership through social network instances, creation, updating active values, archival, immutable network-instance authors, and rejection of unauthorized changes.
- [ ] 5.2 [GREEN] Implement authenticated dashboard workflows and templates for the current user's profile, social network instances, variable values, and archival actions without physical deletion.
- [ ] 5.3 [REFACTOR] Simplify dashboard form, ownership, and archival handling while preserving the passing tests.

## 6. Public presentation

- [ ] 6.1 [RED] Add failing view tests for resolving profiles by `public_username`, rendering public fields and active constructed URLs only, and handling absent profiles.
- [ ] 6.2 [GREEN] Add URL configuration, public profile view, and template using `public_username`.
- [ ] 6.3 [REFACTOR] Simplify presentation queries and templates while preserving the passing view tests.

## 7. Final verification

- [ ] 7.1 Run the complete profiles test suite and resolve any regressions.
- [ ] 7.2 Run Django migrations and `uv run python project/manage.py check`.

For an unplanned task discovered in an implementation child branch, record it as `+=<número>` in that branch's execution tracking without renumbering this approved plan.
