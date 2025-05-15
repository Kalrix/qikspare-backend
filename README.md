
---

## ✅ API Overview

| Endpoint                      | Method | Description                                  | Auth Required | Role     |
|------------------------------|--------|----------------------------------------------|---------------|----------|
| `/auth/request-otp`          | POST   | Send OTP to phone number                     | ❌            | Public   |
| `/auth/verify-otp`           | POST   | Verify OTP and return token                  | ❌            | Public   |
| `/auth/me`                   | GET    | Get current user profile                     | ✅            | All      |
| `/admin/create-user`         | POST   | Create new user (garage, vendor, etc.)       | ✅            | Admin    |
| `/admin/users`               | GET    | Get all users                                | ✅            | Admin    |
| `/admin/user/{user_id}`      | GET    | Get user by ID                               | ✅            | Admin    |
| `/admin/update-user/{id}`    | PATCH  | Update any user by ID                        | ✅            | Admin    |
| `/admin/user/{id}`           | DELETE | Delete any user by ID                        | ✅            | Admin    |
| `/user/update-profile`       | PATCH  | Update logged-in user's profile              | ✅            | All      |
| `/user/add-address`          | POST   | Add address to current user                  | ✅            | All      |
| `/invoices/...`              | ---    | Full invoice management (create/view/edit)   | ✅            | Vendor/Admin |
| `/pin/set`                   | POST   | Set 4-digit PIN after registration           | ✅            | All      |
| `/pin/verify`                | POST   | Login using PIN                              | ❌            | Public   |
| `/pin/reset`                 | POST   | Reset PIN using OTP                          | ❌            | Public   |

---

## 🩺 Health Check

Test that your backend is up and running:

```http
GET /
