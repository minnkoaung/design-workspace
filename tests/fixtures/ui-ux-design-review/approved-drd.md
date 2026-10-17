# Approved DRD — Partner User Administration
Revision: 2.0. Product approval recorded in decisions.md.

## REQ-001 — User list
System Admin sees Name, Mobile Number, Email, Role and Status. Row actions: Edit User and Reset Password. Main action: New User.

## REQ-002 — New User
Fields: Name, Mobile Number, Email and Role. Actions: Create User and Cancel. Email is the username.

## REQ-003 — Edit User
Show current Name, Mobile Number, Email and Role. Name, Mobile Number and Role are editable. Email is read-only in this release. Actions: Save Changes and Cancel.

## REQ-004 — Reset confirmation
Before reset, show the selected user's name and destination email and explain that a temporary password will be emailed. Actions: Reset Password and Cancel.

## REQ-005 — Access
Create, Edit and Reset Password are System Admin only. Portal User has no user-administration access.

## REQ-006 — Temporary password
A temporary password is sent by email after creation or reset. It expires according to the current configured policy. Its duration has not been supplied to Design; do not specify a duration until Product confirms it.

## REQ-007 — Supporting states
Required later: loading, empty list, validation, duplicate email, submission success/failure, email delivery failure and expiry recovery. Their construction scope is determined by the variant decision.
