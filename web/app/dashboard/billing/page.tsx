"use client";

import { DASHBOARD_DATA } from "@/data/dashboard-mock";
import { CreditCard, TrendingUp, Zap, AlertTriangle, ShieldCheck, Clock } from "lucide-react";

export default function BillingPage() {
    return (
        <div className="p-4 md:p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-8 mt-16 md:mt-0">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
                        <CreditCard className="w-8 h-8 text-blue-500" />
                        Value Vault
                    </h1>
                    <p className="text-zinc-500 max-w-xl">
                        Manage your System Capacity (CP). Unlike traditional billing, Side treats capacity as fuel for your strategic engine.
                    </p>
                </div>
                <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-lg">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                    <span className="text-blue-400 font-medium text-sm">{DASHBOARD_DATA.user.planBadge}</span>
                </div>
            </div>

            {/* Main Capacity Card */}
            <div className="bg-[#0c0c0e] border border-white/10 rounded-2xl p-6 md:p-8 relative overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                    {/* Left: Usage Radial/Bar */}
                    <div className="md:col-span-2 flex flex-col justify-between gap-8">
                        <div>
                            <h3 className="text-lg font-medium text-white mb-1">Capacity Fuel</h3>
                            <p className="text-sm text-zinc-500 mb-6"> Monthly refueling cycle resets in {DASHBOARD_DATA.capacity.resetTime}.</p>

                            {/* Big Progress Bar (Segmented Style) */}
                            <div className="flex bg-zinc-800/30 rounded-full h-4 overflow-hidden p-[2px] gap-[2px] mb-2">
                                {[...Array(40)].map((_, i) => {
                                    const percentage = (DASHBOARD_DATA.capacity.used / DASHBOARD_DATA.capacity.limit) * 100;
                                    const blockValue = 100 / 40; // 2.5% per block
                                    const isFilled = percentage >= (i + 1) * blockValue;

                                    return (
                                        <div
                                            key={i}
                                            className={`flex-1 rounded-[1px] transition-all duration-300 ${isFilled ? "bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" : "bg-white/5"
                                                }`}
                                        />
                                    )
                                })}
                            </div>
                            <div className="flex justify-between text-xs font-mono text-zinc-500 uppercase tracking-widest">
                                <span>Used: {DASHBOARD_DATA.capacity.used.toLocaleString()} CP</span>
                                <span>Limit: {DASHBOARD_DATA.capacity.limit.toLocaleString()} CP</span>
                            </div>
                        </div>

                        {/* Breakdown */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-zinc-900/50 rounded-lg p-3 border border-white/5">
                                <span className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                                    <ShieldCheck className="w-3 h-3" /> Audits
                                </span>
                                <div className="text-xl font-bold text-white">{DASHBOARD_DATA.capacity.breakdown.audits.toLocaleString()} <span className="text-xs font-normal text-zinc-600">CP</span></div>
                            </div>
                            <div className="bg-zinc-900/50 rounded-lg p-3 border border-white/5">
                                <span className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                                    <Zap className="w-3 h-3" /> Quick Ops
                                </span>
                                <div className="text-xl font-bold text-white">{DASHBOARD_DATA.capacity.breakdown.quickOps.toLocaleString()} <span className="text-xs font-normal text-zinc-600">CP</span></div>
                            </div>
                            <div className="bg-zinc-900/50 rounded-lg p-3 border border-white/5">
                                <span className="flex items-center gap-2 text-xs text-zinc-400 mb-1">
                                    <Clock className="w-3 h-3" /> Runway
                                </span>
                                <div className="text-xl font-bold text-emerald-400">High <span className="text-xs font-normal text-zinc-600">Velocity</span></div>
                            </div>
                        </div>
                    </div>

                    {/* Right: Actions & Plans */}
                    <div className="border-l border-white/10 pl-0 md:pl-12 flex flex-col justify-between gap-8 h-full">
                        <div>
                            <h3 className="text-sm font-medium text-zinc-400 mb-4 uppercase tracking-widest">Select Capacity Plan</h3>
                            <div className="space-y-3">
                                <div className="p-3 rounded-lg border border-white/10 bg-white/5 flex justify-between items-center cursor-pointer hover:bg-white/10 transition-colors">
                                    <div>
                                        <div className="text-white font-medium text-sm">Starter Capacity</div>
                                        <div className="text-xs text-zinc-500">2,000 CP / month</div>
                                    </div>
                                    <div className="text-zinc-400 text-sm">$0</div>
                                </div>
                                <div className="p-3 rounded-lg border border-blue-500/30 bg-blue-500/10 flex justify-between items-center cursor-pointer ring-1 ring-blue-500/50 relative">
                                    <div className="absolute -top-2 -right-2 bg-blue-500 text-[10px] text-white px-2 py-0.5 rounded-full">ACTIVE</div>
                                    <div>
                                        <div className="text-white font-medium text-sm">High Octane</div>
                                        <div className="text-xs text-blue-300/70">10,000 CP / month</div>
                                    </div>
                                    <div className="text-white text-sm font-bold">$20</div>
                                </div>
                                <div className="p-3 rounded-lg border border-white/10 bg-white/5 flex justify-between items-center cursor-pointer hover:bg-white/10 transition-colors opacity-50">
                                    <div>
                                        <div className="text-white font-medium text-sm">Sovereign Cluster</div>
                                        <div className="text-xs text-zinc-500">Unlimited Local CP</div>
                                    </div>
                                    <div className="text-zinc-400 text-sm">Custom</div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3 pt-4 border-t border-white/10">
                            <button
                                onClick={() => alert("Refueling Initiated.")}
                                className="w-full bg-white text-black hover:bg-zinc-200 font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
                            >
                                <Zap className="w-4 h-4 text-black" /> Instant Refuel
                            </button>
                            <div className="text-center">
                                <span className="text-xs text-zinc-500">Unbilled: </span>
                                <span className="text-white font-mono text-sm">${DASHBOARD_DATA.capacity.unbilled.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Invoices / History */}
            <div>
                <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-zinc-500" /> Refuel History
                </h3>
                <div className="border border-white/10 rounded-xl overflow-hidden">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-zinc-900/50 text-zinc-500 font-mono uppercase text-xs">
                            <tr>
                                <th className="px-6 py-3 font-normal">Date</th>
                                <th className="px-6 py-3 font-normal">Description</th>
                                <th className="px-6 py-3 font-normal text-right">Amount</th>
                                <th className="px-6 py-3 font-normal text-right">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 bg-[#0c0c0e]">
                            <tr>
                                <td className="px-6 py-4 text-zinc-300 font-mono">Oct 01, 2024</td>
                                <td className="px-6 py-4 text-white">Monthly Base Capacity (PRO)</td>
                                <td className="px-6 py-4 text-right text-zinc-300">$20.00</td>
                                <td className="px-6 py-4 text-right"><span className="text-emerald-400 text-xs bg-emerald-500/10 px-2 py-1 rounded">Paid</span></td>
                            </tr>
                            <tr>
                                <td className="px-6 py-4 text-zinc-300 font-mono">Sep 01, 2024</td>
                                <td className="px-6 py-4 text-white">Monthly Base Capacity (PRO)</td>
                                <td className="px-6 py-4 text-right text-zinc-300">$20.00</td>
                                <td className="px-6 py-4 text-right"><span className="text-emerald-400 text-xs bg-emerald-500/10 px-2 py-1 rounded">Paid</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Alert Banner */}
            <div className="bg-yellow-500/5 border border-yellow-500/10 p-4 rounded-lg flex items-start gap-4">
                <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                <div>
                    <h4 className="text-yellow-200 font-medium text-sm mb-1">Capacity Optimization Tip</h4>
                    <p className="text-zinc-400 text-xs leading-relaxed">
                        Your audit frequency is high. Consider switching to "Batch Mode" in <span className="font-mono text-white bg-white/10 px-1 rounded">settings</span> to save roughly 300 CP per week without losing strategic coverage.
                    </p>
                </div>
            </div>
        </div >
    );
}
