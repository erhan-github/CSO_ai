export const DASHBOARD_DATA = {
    user: {
        plan: "PRO Tier",
        planBadge: "PRO Plan Active",
        status: "High Velocity",
    },
    capacity: {
        used: 1550,
        limit: 10000,
        unbilled: 12.40,
        breakdown: {
            audits: 1200,
            quickOps: 350,
        },
        resetTime: "12 days",
    },
    auditLog: [
        { id: 1, timestamp: "Oct 24, 10:42 AM", operation: "AUDIT", subject: "src/auth/login.ts", model: "claude-3-5-sonnet", tokens: 4200, cpCost: 500, estCost: 0.15, status: "success" },
        { id: 2, timestamp: "Oct 24, 10:30 AM", operation: "PLAN", subject: "Architecture Review", model: "gpt-4o", tokens: 1200, cpCost: 100, estCost: 0.03, status: "success" },
        { id: 3, timestamp: "Oct 24, 09:15 AM", operation: "SIMULATE", subject: "User Journey: Onboarding", model: "groq-llama-3-70b", tokens: 15600, cpCost: 300, estCost: 0.09, status: "success" },
        { id: 4, timestamp: "Oct 24, 08:55 AM", operation: "REFUEL", subject: "Capacity Top-up", model: "system", tokens: 0, cpCost: 0, estCost: 20.00, status: "success" },
        { id: 5, timestamp: "Oct 23, 04:20 PM", operation: "AUDIT", subject: "components/ui/button.tsx", model: "claude-3-haiku", tokens: 840, cpCost: 50, estCost: 0.01, status: "warning" },
        { id: 6, timestamp: "Oct 23, 02:10 PM", operation: "CHAT", subject: "Explanation of useEffect", model: "gpt-4o-mini", tokens: 540, cpCost: 20, estCost: 0.01, status: "success" },
    ]
};
