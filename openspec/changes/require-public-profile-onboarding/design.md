## Context

`PublicProfile` is an existing one-to-one extension of the authentication user, while the project currently exposes only the staff-oriented Django admin site. There is no self-service profile route, login endpoint, or dashboard. The new flow uses Django admin's bundled views, styles, and form components, with one scoped admin template override for the public-profile form. See `proposal.md` and the two specification deltas for the required behavior.

## Goals / Non-Goals

**Goals:**
- Provide one authenticated self-service admin flow from login to either profile onboarding or the dashboard.
- Ensure profile ownership is derived from the authenticated request rather than client-submitted data.
- Prevent dashboard content from being reached before the required public profile exists.
- Preserve the current `PublicProfile` fields and validation rules while exposing them through Django admin's native creation form.
- Apply the profile gate consistently to ordinary, staff, and superuser accounts.

**Non-Goals:**
- Public presentation pages, arbitrary project-owned HTML templates, API endpoints, social-link management, or dashboard business features beyond the access boundary.
- Creating profiles automatically or inferring missing public field values.
- Changing the user model or migrating existing `PublicProfile` records.

## Decisions

### Use a dedicated self-service AdminSite as the dashboard

The project will add a dedicated `AdminSite` for self-service profile onboarding, separate from Django's existing staff admin site. Its native login view and index will supply the login and dashboard UI. The site's permission check will accept every active authenticated account, not only staff or superusers. A centralized route guard will redirect every authenticated user without a profile from any dashboard route to the native `PublicProfile` add view, except the add view itself and logout. Users with a profile receive the normal admin index. Reusing the existing staff admin site was rejected because ordinary authenticated users cannot access it and staff privileges must not bypass the profile requirement.

### Restrict the self-service site to the current user's profile

Only `PublicProfile` will be registered in the self-service site. Its `ModelAdmin` will return only the profile associated with the current request user, allow creation only when that user has no profile, and allow changes only to that user's own profile. This keeps the admin index useful as a dashboard without exposing other profiles or unrelated models. Granting the full staff admin registry to normal users was rejected because it would expose administrative capabilities outside the change's scope.

### Reuse a readable admin ModelForm and derive ownership on the server

The `ModelAdmin` will use a dedicated `ModelForm` that lists only editable public-profile fields and omits `user`. The admin will inject `request.user` when it creates the form so the form can initialize `public_username`, `first_name`, and `last_name` from the authentication account; these are editable defaults, not ownership inputs. Its save hook will set the relationship from `request.user`, and change views will expose that relationship as read-only. The native admin add/change views render the form, labels, errors, controls, and styles. One `change_form` template override is permitted solely to remove breadcrumbs and the sidebar while retaining the standard top navbar and logout action. Trusting a hidden user identifier was rejected because clients can alter hidden fields; a broader custom template was rejected because it duplicates Django admin UI.

### Keep the dashboard intentionally minimal

The self-service admin index will be the dashboard. It confirms the completed onboarding state and provides a stable entry point for future self-service features. Building a separate dashboard view or page was rejected because no behavior beyond access control is required and it would require project-owned presentation.

### Add focused request-level tests

Tests will use Django's test client to exercise the dedicated site's login outcomes, index redirects, native add form rendering and submission, invalid submissions, and cross-user ownership attempts for ordinary, staff, and superuser accounts. Model/admin tests will cover the form field set and per-user query/permission behavior. Unit-only mocks were rejected because admin-site routing, sessions, and object permissions require request/database integration to validate the contract.

## Risks / Trade-offs

- [An existing user has no profile] -> The centralized dashboard guard routes the user to onboarding rather than showing any dashboard route; no profile is silently fabricated.
- [A client submits a forged user identifier] -> The admin form does not expose the field and the admin save hook always assigns `request.user`.
- [A user opens onboarding after completion] -> The self-service permissions deny a second add and direct the user to their existing profile/dashboard.
- [Global guard redirects the user away from onboarding or logout] -> Explicitly exempt the native add and logout routes from the profile requirement.
- [An ordinary user sees another profile] -> The `ModelAdmin` queryset and object permissions are restricted to the session user's profile.
- [The staff site bypasses onboarding] -> The self-service dashboard enforces the gate for every account type; privileged staff administration remains a separate concern.

## Migration Plan

1. Add the self-service admin site, URL registration, global profile guard, profile admin form, limited form-template override, and ownership protections without changing the database schema.
2. Deploy and verify that ordinary, staff, and superuser accounts without a profile are redirected from every protected dashboard route to onboarding, can still submit the form or log out, then gain dashboard access after valid submission.
3. Verify existing users with a profile can log in and reach the self-service dashboard immediately.
4. Roll back application code if needed; existing profile records and user associations remain unchanged because this change has no data migration.
