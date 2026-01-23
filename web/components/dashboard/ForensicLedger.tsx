import { DASHBOARD_DATA } from "@/data/dashboard-mock";
import { FileText, MoreHorizontal, Download, Filter } from "lucide-react";

export function ForensicLedger() {
    return (
        <div className="bg-[#0c0c0e] border border-white/10 rounded-xl overflow-hidden flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-zinc-900/30 backdrop-blur-sm">
                <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-medium text-white">Forensic Ledger</h3>
                </div>

                <div className="flex items-center gap-2">
                    <button className="p-1.5 hover:bg-white/5 border border-transparent hover:border-white/10 rounded-md text-zinc-500 hover:text-white transition-all">
                        <Filter className="w-3.5 h-3.5" />
                    </button>
                    <button className="p-1.5 hover:bg-white/5 border border-transparent hover:border-white/10 rounded-md text-zinc-500 hover:text-white transition-all">
                        <Download className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto flex-1">
                <table className="w-full text-left text-sm">
                    <thead>
                        <tr className="border-b border-white/5 text-xs text-zinc-500 font-mono uppercase tracking-wider">
                            <th className="px-5 py-3 font-normal">Time</th>
                            <th className="px-5 py-3 font-normal">Operation</th>
                            <th className="px-5 py-3 font-normal">Model Inference</th>
                            <th className="px-5 py-3 font-normal text-right">Cost (CP)</th>
                            <th className="px-5 py-3 font-normal text-right">Est. Cost ($)</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {DASHBOARD_DATA.auditLog.map((entry, i) => (
                            <tr key={i} className="group hover:bg-white/[0.02] transition-colors">
                                <td className="px-5 py-2.5 font-mono text-zinc-400 text-xs whitespace-nowrap">
                                    {entry.timestamp}
                                </td>
                                <td className="px-5 py-3">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border uppercase tracking-wide
                     ${entry.operation === 'AUDIT' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                            entry.operation === 'PLAN' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                                'bg-purple-500/10 text-purple-400 border-purple-500/20'
                                        }`}>
                                        {entry.operation}
                                    </span>
                                </td>
                                <td className="px-5 py-3">
                                    <div className="flex flex-col">
                                        <span className="text-zinc-300 font-mono text-xs">{entry.model}</span>
                                    </div>
                                </td>
                                <td className="px-5 py-3 text-right font-mono text-zinc-300">
                                    -{entry.cpCost}
                                </td>
                                <td className="px-5 py-3 text-right font-mono text-zinc-500">
                                    ${entry.estCost.toFixed(4)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Footer / Pagination */}
            <div className="p-3 border-t border-white/5 flex justify-center">
                <button className="text-xs text-zinc-500 hover:text-white transition-colors">View All History</button>
            </div>
        </div>
    );
}
