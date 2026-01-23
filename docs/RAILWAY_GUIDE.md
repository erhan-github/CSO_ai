# 🚂 Railway Production Cheat Sheet

Here are all the settings you need to configure in the Railway Dashboard to get **Sidelith** live.

---

## 🏗️ 1. Backend Service (`/backend`)
Railway will auto-detect the `Dockerfile` and build it.

### **Variables (Copy-Paste)**

| Variable Name | Value (Sourced from .env) |
| :--- | :--- |
| `PORT` | `8000` |
| `MCP_TRANSPORT` | `sse` (**Critical** for Dashboard access) |
| `GROQ_API_KEY` | `REDACTED_GROQ_KEY` |
| `SUPABASE_URL` | `https://mudprpfsajbjjixprluj.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (See .env) |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (See .env.local) |
| `SIDE_API_KEY` | `REDACTED_API_KEY` |
| `POSTHOG_API_KEY` | `REDACTED_POSTHOG_KEY` |
| `PYTHONPATH` | `/app/src` |

### **Settings**
*   **Networking**: Ensure Public Networking is **Enabled**.
*   **Health Check**: Path: `/sse`, Timeout: `100s`.

---

## 🌐 2. Frontend Service (`/web`)
Railway will use **Nixpacks** to build the Next.js app.

### **Variables (Copy-Paste)**

| Variable Name | Value (Sourced from .env.local) |
| :--- | :--- |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://mudprpfsajbjjixprluj.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `LEMONSQUEEZY_API_KEY` | `eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...` |
| `LEMONSQUEEZY_STORE_ID` | `277583` |
| `LEMONSQUEEZY_VARIANT_ID_PRO` | `v1240865` |
| `LEMONSQUEEZY_VARIANT_ID_ELITE` | `1240924` |
| `LEMONSQUEEZY_VARIANT_ID_REFILL` | `1240928` |
| `LEMONSQUEEZY_WEBHOOK_SECRET` | `karamela_sepeti_2026_xyz` |

### **Settings**
*   **Build Command**: `npm run build`
*   **Start Command**: `npm run start`

---

## 🚀 Final Step: Verification
Once both services are "Active" (Green) in Railway:

1.  Visit your **Frontend URL** (e.g., `sidelith-web.up.railway.app`).
2.  Login via GitHub.
3.  Check the **Forensic Ledger**. It should now sync data from the cloud, and you'll see your `sk_live` key in the Registry Credentials.

---
*Side - Ready for Egress.*
