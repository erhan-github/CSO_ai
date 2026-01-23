import { StrategicErrorBoundary } from "@/components/observability/ErrorBoundary";
import { GlobalSidebar } from "@/components/dashboard/GlobalSidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen bg-[#000000] text-foreground">
            <GlobalSidebar />
            <main className="flex-1 overflow-y-auto h-screen bg-[#050505]">
                <StrategicErrorBoundary>
                    {children}
                </StrategicErrorBoundary>
            </main>
        </div>
    );
}
