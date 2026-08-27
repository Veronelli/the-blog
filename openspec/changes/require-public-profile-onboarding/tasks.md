## 1. Self-Service Django Admin

- [x] 1.1 Add a dedicated self-service `AdminSite` that accepts every active authenticated account and routes users without a `PublicProfile` from its index to onboarding.
- [x] 1.2 Register only `PublicProfile` in the self-service site and add a readable admin `ModelForm` containing every editable profile field and no authentication-user field.
- [x] 1.3 Configure the profile `ModelAdmin` to assign `request.user` on creation, keep ownership read-only on change, and preserve the original association.
- [x] 1.4 Restrict the profile `ModelAdmin` queryset and add/change permissions so users can create only their own missing profile and access only their own existing profile.

## 2. Native Admin Routing

- [ ] 2.1 Register the self-service admin URLs and use a centralized guard to redirect users without a profile from every dashboard route to onboarding, except the native add and logout routes.
- [ ] 2.2 Use Django admin's bundled templates, styles, form components, and validation errors; add the limited `PublicProfile` form override that hides breadcrumbs and the sidebar while retaining logout.

## 3. Flow Verification

- [ ] 3.1 Add request-level tests for unauthenticated access and every protected dashboard route for ordinary, staff, and superuser accounts with and without profiles.
- [ ] 3.2 Add request-level tests that verify valid native-admin onboarding assigns the session user, invalid submissions remain blocked from the dashboard, submitted user identifiers cannot change ownership, and logout remains available before onboarding.
- [ ] 3.3 Add request-level tests that verify a user cannot list, view, edit, or create a profile for another user through the self-service site.
- [ ] 3.4 Run `uv run python project/manage.py test` and `uv run python project/manage.py check`.
