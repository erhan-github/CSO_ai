"use client";

import { Shield, Eye, Lock, Globe, Server, Trash2, Power, Download } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
    const [ghostMode, setGhostMode] = useState(false);

    return (
        <div className="p-4 md:p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-8 mt-16 md:mt-0">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
                        <Shield className="w-8 h-8 text-emerald-500" />
                        Privacy & Data
                    </h1>
                    <p className="text-zinc-300 max-w-xl font-medium">
                        Sovereign control over your context. Sidelith is designed to be "Local First", giving you absolute authority over data egress.
                    </p>
                </div>
            </div>

            {/* Ghost Mode Toggle (Hero Feature) */}
            <div className={cn(
                "border rounded-2xl p-6 md:p-8 transition-all duration-300 relative overflow-hidden",
                ghostMode ? "bg-emerald-950/10 border-emerald-500/30" : "bg-[#0c0c0e] border-white/10"
            )}>
                {ghostMode && (
                    <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none" />
                )}

                <div className="flex flex-col md:flex-row justify-between items-center gap-8 relative z-10">
                    <div className="flex-1">
                        <h3 className="text-xl font-bold text-white flex items-center gap-3 mb-2">
                            <Eye className={cn("w-6 h-6", ghostMode ? "text-emerald-400" : "text-zinc-500")} />
                            Ghost Mode
                            {ghostMode && <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded border border-emerald-500/30">ACTIVE</span>}
                        </h3>
                        <p className="text-zinc-400 text-sm leading-relaxed max-w-2xl">
                            When active, Sidelith creates an "air gap" for your intelligence. All external API calls (Anthropic, OpenAI) are intercepted.
                            Inference is routed strictly to your local models or secure cached snapshots.
                        </p>
                    </div>

                    <button
                        onClick={() => setGhostMode(!ghostMode)}
                        className={cn(
                            "relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2 focus:ring-offset-black",
                            ghostMode ? "bg-emerald-600" : "bg-zinc-700"
                        )}
                    >
                        <span className={cn(
                            "pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
                            ghostMode ? "translate-x-6" : "translate-x-0"
                        )} />
                    </button>
                </div>
            </div>

            {/* Data Sovereignty Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Telemetry Control */}
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5">
                                <Globe className="w-5 h-5 text-blue-400" />
                            </div>
                            <div>
                                <h3 className="text-white font-bold">Judicial Cloud Sync</h3>
                                <p className="text-xs text-zinc-500 font-medium">Data sent to Sidelith Registry</p>
                            </div>
                        </div>
                        <div className="text-3xl font-black font-mono text-white mb-1">100 <span className="text-zinc-500 text-lg uppercase tracking-tighter">%</span></div>
                        <div className="h-2 w-full bg-zinc-800 rounded-full mt-4 overflow-hidden border border-white/5">
                            <div className="h-full bg-blue-500 w-full" />
                        </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-white/5">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-zinc-400">Crash Reports</span>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-emerald-500">Disabled</span>
                                <Power className="w-4 h-4 text-emerald-500" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Local Storage */}
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5">
                                <Server className="w-5 h-5 text-zinc-400" />
                            </div>
                            <div>
                                <h3 className="text-white font-medium">Local Intelligence</h3>
                                <p className="text-xs text-zinc-500">Stored on device (~/.side/data)</p>
                            </div>
                        </div>
                        <div className="text-3xl font-mono text-white mb-1">142 <span className="text-zinc-600 text-lg">MB</span></div>
                        <div className="flex gap-1 mt-4">
                            <div className="h-1 bg-purple-500 w-[60%] rounded-l-full" />
                            <div className="h-1 bg-blue-500 w-[30%]" />
                            <div className="h-1 bg-zinc-700 w-[10%] rounded-r-full" />
                        </div>
                        <div className="flex justify-between text-[10px] text-zinc-500 mt-2 font-mono uppercase">
                            <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" /> Embeddings</span>
                            <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> Context</span>
                            <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-zinc-700" /> Logs</span>
                        </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-white/5 flex gap-3">
                        <button className="flex-1 bg-white/5 hover:bg-white/10 text-white text-xs font-medium py-2 rounded border border-white/5 transition-colors flex items-center justify-center gap-2">
                            <Download className="w-3 h-3" /> Export
                        </button>
                    </div>
                </div>
            </div>

            {/* Danger Zone */}
            <div className="border border-red-900/30 bg-red-950/5 rounded-xl p-6">
                <h3 className="text-red-400 font-bold mb-4 flex items-center gap-2">
                    <AlertTriangleIcon /> Danger Zone
                </h3>

                <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="text-sm text-zinc-400 max-w-2xl">
                        <strong className="text-red-200 block mb-1">Purge Registry Intelligence</strong>
                        Irreversibly wipe all context associated with your workspace from Sidelith's remote registry.
                        This does not affect your local project snapshots.
                    </div>
                    <button
                        onClick={() => confirm("Are you absolutely sure? This action cannot be undone.") && alert("Purge request initiated. This may take up to 24 hours.")}
                        className="bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 px-4 py-2 rounded-lg text-sm font-black transition-colors flex items-center gap-2 whitespace-nowrap uppercase italic tracking-tighter"
                    >
                        <Trash2 className="w-4 h-4" /> Purge Cloud Registry
                    </button>
                </div>
            </div>
        </div>
    );
}

function AlertTriangleIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><path d="M12 9v4" /><path d="M12 17h.01" /></svg>
    )
}
