import { useState } from "react";
import { ChevronDown, ChevronUp, Code2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ProofViewerProps {
    leanCode: string;
    title?: string;
    defaultExpanded?: boolean;
}

/**
 * ProofViewer - Displays Lean 4 proofs with syntax highlighting
 * 
 * Highlights:
 * - Keywords (theorem, def, by, sorry, etc.)
 * - Comments (-- lines)
 * - Types (Int, List, Bool, etc.)
 * - `sorry` lines are highlighted in red as errors
 */
export default function ProofViewer({ leanCode, title = "Formal Proof (Lean 4)", defaultExpanded = false }: ProofViewerProps) {
    const [expanded, setExpanded] = useState(defaultExpanded);

    const highlightLean = (code: string) => {
        const lines = code.split('\n');

        return lines.map((line, idx) => {
            const trimmed = line.trim();

            // Check if line contains 'sorry' (error)
            const isSorryLine = trimmed.includes('sorry');

            // Check if line is a comment
            const isComment = trimmed.startsWith('--');

            // Apply syntax highlighting
            let highlighted = line
                // Keywords
                .replace(/\b(theorem|def|lemma|by|sorry|import|where|if|then|else|match|with|let|in|have|show|case|exact|apply|intro|simp|omega|linarith|split_ifs|unfold|rfl|trivial|decide|native_decide)\b/g,
                    '<span class="text-purple-400 font-bold">$1</span>')
                // Types
                .replace(/\b(Int|Nat|Bool|String|List|Option|Float|Prop|Type)\b/g,
                    '<span class="text-blue-400">$1</span>')
                // Arrow operators
                .replace(/([→←↔∈∉∧∨¬≤≥≠])/g,
                    '<span class="text-yellow-400">$1</span>')
                // Comments
                .replace(/(--.*)/g,
                    '<span class="text-green-400 italic">$1</span>')
                // Numbers
                .replace(/\b(\d+)\b/g,
                    '<span class="text-orange-400">$1</span>');

            // Base classes
            let lineClasses = "block px-4 py-0.5 hover:bg-gray-800/50";

            // Sorry lines get red background
            if (isSorryLine) {
                lineClasses += " bg-red-900/30 border-l-2 border-red-500";
            }

            // Comment lines get subtle green tint
            if (isComment) {
                lineClasses += " bg-green-900/10";
            }

            return (
                <div
                    key={idx}
                    className={lineClasses}
                    dangerouslySetInnerHTML={{ __html: highlighted || '&nbsp;' }}
                />
            );
        });
    };

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <div
                className="p-3 flex items-center justify-between cursor-pointer bg-gray-800/50 hover:bg-gray-800"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center space-x-3">
                    <Code2 className="w-5 h-5 text-purple-400" />
                    <h4 className="text-sm font-bold text-gray-200">{title}</h4>
                </div>
                {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                    >
                        <div className="max-h-96 overflow-auto bg-black/50 font-mono text-xs leading-relaxed">
                            {/* Line numbers */}
                            <div className="flex">
                                <div className="text-gray-600 text-right pr-2 border-r border-gray-800 select-none">
                                    {leanCode.split('\n').map((_, idx) => (
                                        <div key={idx} className="px-2 py-0.5">
                                            {idx + 1}
                                        </div>
                                    ))}
                                </div>
                                <div className="flex-1">
                                    {highlightLean(leanCode)}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
