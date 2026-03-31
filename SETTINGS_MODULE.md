# Settings Module Documentation

A comprehensive settings module with tabbed interface for managing all aspects of the fleet tracking system.

## 📑 Overview

The Settings module is organized into 6 main tabs:
1. **General** - Company information and branding
2. **Profile** - Personal user information
3. **Camera** - Camera & video settings with AI detection
4. **Notifications** - Alert and notification preferences
5. **Security** - Password and account security
6. **Team** - Team member management and roles

## 🎯 Features by Tab

### 1. General Settings

**Company Information:**
- Company name
- Email and phone
- Physical address
- City and country
- Company description

**Branding:**
- Logo upload (PNG/JPG, up to 2MB, 400x400px recommended)
- Logo preview

**Localization:**
- Timezone selection (East Africa Time, West Africa Time, etc.)
- Currency (KES, TZS, UGX, USD, EUR)
- Language (English, Swahili, French)

**Default Values:**
- Company: Fleet Logistics Kenya
- Location: Industrial Area, Nairobi
- Timezone: Africa/Nairobi (EAT)
- Currency: KES (Kenyan Shilling)

### 2. Profile Settings

**Personal Information:**
- Full name
- Email (read-only, managed by auth)
- Phone number
- Job title
- Department

**Profile Picture:**
- Avatar upload
- Image preview
- Automatic fallback with initials

**Integration:**
- Connected to Supabase auth
- Syncs with profiles table
- Real-time updates

### 3. Notification Settings

**Notification Channels:**
- ✉️ Email notifications
- 🔔 Push notifications
- 💬 SMS notifications

**Alert Preferences:**
- 🚛 Vehicle alerts (status changes)
- ⚠️ Maintenance reminders
- 📦 Delivery updates
- 💬 Driver messages
- 🚨 System alerts

**Reports:**
- Weekly fleet summary
- Monthly performance reports

**Features:**
- Toggle switches for each preference
- Granular control over notifications
- Save preferences to backend

### 4. Security Settings

**Password Management:**
- Change password form
- Current password verification
- New password confirmation
- Validation (min 6 characters)

**Two-Factor Authentication:**
- Enable/disable 2FA
- Configuration interface (coming soon)
- Extra security layer

**Session Management:**
- View active sessions
- Device and location info
- Sign out all other sessions

**Danger Zone:**
- Account deletion
- Irreversible action warning
- Confirmation required

### 3. Camera & Video Settings

**Camera System:**
- Master enable/disable switch
- System-wide camera control

**Video Quality:**
- Resolution: 720p, 1080p, 1440p (2K), 2160p (4K)
- Bitrate: 500-8000 kbps (adjustable slider)
- Frame Rate: 15, 24, 30, 60 FPS
- Quality recommendations based on resolution

**Upload Settings:**
- **Real-time:** Continuous streaming (high bandwidth)
- **On Event:** Upload when AI detects incidents (recommended)
- **Periodic:** Scheduled intervals (15min, 30min, hourly, daily)
- **Manual:** Upload only when requested
- Upload quality: Low (compressed), Medium (balanced), High (original)

**AI Detection Rules:**
- Master AI enable/disable switch
- **Driver Drowsiness Detection** - Detect signs of fatigue
- **Lane Departure Warning** - Alert when drifting from lane
- **Distracted Driving Detection** - Phone use, eating, distractions
- **Collision Warning** - Forward collision and obstacle detection
- **Speeding Alert** - Exceed speed limit warnings
- **Harsh Braking Detection** - Sudden or aggressive braking

**Storage Settings:**
- Duration: 7, 14, 30, 60, 90, 180, 365 days
- Cloud Providers:
  - **Amazon S3** - Reliable, scalable
  - **Wasabi** - Cost-effective S3-compatible
  - **MinIO** - Self-hosted object storage
  - **Azure Blob Storage** - Microsoft cloud
  - **Google Cloud Storage** - Google's object storage
- Local backup option
- Storage cost estimator

**Advanced Settings:**
- Night vision mode
- Audio recording
- GPS overlay (location & speed)
- Timestamp overlay
- Privacy compliance warnings

**Features:**
- Estimated storage cost calculator
- Test camera functionality
- Important notes and warnings
- Bandwidth and storage impact indicators

### 4. Notification Settings

**Team Members Table:**
- Member name and avatar
- Email address
- Role badge (Admin, Fleet Manager, Driver, Viewer)
- Status (Active/Pending)
- Actions menu

**Invite Members:**
- Email invitation dialog
- Role selection
- Send invitation via email
- Pending invitation tracking

**Role Management:**
- **Admin** - Full access to all features
- **Fleet Manager** - Manage vehicles, drivers, routes
- **Driver** - Update delivery status, communicate
- **Viewer** - Read-only access

**Actions:**
- Invite new members
- Resend invitations
- Change member roles
- Remove members

**Sample Team:**
- Kamau Mwangi (Admin)
- Mary Njeri (Fleet Manager)
- John Omondi (Driver)
- Peter Wanjiru (Viewer - Pending)

## 🎨 UI Components Used

- **Tabs** - Main navigation
- **Cards** - Content sections
- **Forms** - Data input with validation
- **Switches** - Toggle preferences
- **Dialogs** - Modal interactions
- **Tables** - Team member list
- **Badges** - Status and role indicators
- **Avatars** - User profile pictures
- **Dropdowns** - Action menus

## 🔧 Technical Implementation

### File Structure:
```
src/
├── pages/
│   └── Settings.tsx (Main settings page with tabs)
└── components/
    └── settings/
        ├── GeneralSettings.tsx
        ├── ProfileSettings.tsx
        ├── CameraSettings.tsx (NEW)
        ├── NotificationSettings.tsx
        ├── SecuritySettings.tsx
        └── TeamSettings.tsx
```

### Form Validation:
- **Zod** schemas for type-safe validation
- **React Hook Form** for form management
- Real-time error messages
- Field-level validation

### State Management:
- Local state with useState
- Form state with useForm
- Toast notifications for feedback

### Backend Integration:
- Supabase Auth for user management
- Profiles table for user data
- Real-time updates
- Secure password changes

## 🚀 Access

Navigate to: **http://localhost:5173/settings**

Or click the **Settings** icon in the navigation sidebar.

## 📱 Responsive Design

- Mobile-friendly layout
- Responsive grid columns
- Touch-friendly controls
- Adaptive spacing

## 🔐 Security Features

- Password strength validation
- Secure password updates via Supabase Auth
- Session management
- 2FA support (coming soon)
- Account deletion safeguards

## 🌍 Localization Support

**Timezones:**
- East Africa Time (EAT)
- West Africa Time (WAT)
- Egypt Time (EET)
- South Africa Time (SAST)

**Currencies:**
- KES - Kenyan Shilling
- TZS - Tanzanian Shilling
- UGX - Ugandan Shilling
- USD - US Dollar
- EUR - Euro

**Languages:**
- English
- Swahili
- French

## 📊 Future Enhancements

- [ ] API integration for all settings
- [ ] Real-time team member sync
- [ ] 2FA implementation
- [ ] Activity logs
- [ ] Audit trail
- [ ] Role-based access control enforcement
- [ ] Bulk team member import
- [ ] Custom role creation
- [ ] Email template customization
- [ ] Webhook configuration

## 💡 Usage Tips

1. **Save frequently** - Changes are saved per tab
2. **Test notifications** - Use test buttons to verify settings
3. **Invite carefully** - Review roles before sending invitations
4. **Backup data** - Export settings before major changes
5. **Review sessions** - Regularly check active sessions

All settings are designed to be intuitive and user-friendly while providing comprehensive control over the fleet tracking system.
