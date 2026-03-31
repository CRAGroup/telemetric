# Test User Credentials

## ✅ Authentication System is Working!

You successfully logged in with: **admin@admin123.com**

## Current Test Account

- **Email:** admin@admin123.com
- **Password:** (your password)
- **Status:** ✅ Active and working

## Create Additional Users

You can create more users through the signup page:

1. Visit: http://localhost:5173/signup
2. Enter details (use real email domains like @gmail.com, @yahoo.com, etc.)
3. Click "Create Account"
4. Login immediately (email confirmation is disabled)

## Authentication Features

The system includes:
- ✅ **Login/Signup** - Full authentication flow
- ✅ **Protected Routes** - Dashboard requires authentication
- ✅ **Session Management** - Stay logged in across refreshes
- ✅ **User Menu** - Profile, settings, and logout
- ✅ **Auto Profile Creation** - Profiles created on signup
- ✅ **Role Assignment** - Default "viewer" role for new users
- ✅ **Toast Notifications** - Success/error messages

## Access Your Dashboard

**http://localhost:5173/**

- If not logged in → redirected to `/login`
- After login → access full dashboard
- Click avatar in sidebar → user menu with logout

## Notes

- Email confirmation is currently **disabled** for easier testing
- Use real email domains (not @example.com) when creating accounts
- All new users get "viewer" role by default
- Admins can be assigned through the database or future admin panel
