import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, FileCode, Lightbulb, Loader2 } from "lucide-react";
import CodeEditor from "./CodeEditor";
import ProofViewer from "./ProofViewer";

interface FileResult {
    filename: string;
    status: string;
    verified: boolean;
    fix_verified: boolean;
    original_code: string;
    fixed_code: string;
    logs: string[];
    // New fields from enhanced report
    error_explanation?: string;
    counterexample?: Record<string, number | string>;
    lean_proof?: string;
}

export default function FileResultCard({ result }: { result: FileResult }) {
    const [expanded, setExpanded] = useState(false);
    const [aiExplanation, setAiExplanation] = useState<string | null>(null);
    const [isExplaining, setIsExplaining] = useState(false);

    // Derived Status Logic
    const isSecure = result.verified;
    const isPatched = !result.verified && result.fix_verified && result.fixed_code && result.fixed_code !== result.original_code;
    const isVulnerable = !isSecure && !isPatched;

    const getStatusBadge = () => {
        if (isSecure) {
            return (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-900/50 text-green-400 border border-green-800">
                    SECURE
                </span>
            );
        }
        if (isPatched) {
            return (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-yellow-900/50 text-yellow-400 border border-yellow-800">
                    AUTO-PATCHED
                </span>
            );
        }
        return (
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-900/50 text-red-400 border border-red-800">
                VULNERABLE
            </span>
        );
    };

    const askGemini = async () => {
        setIsExplaining(true);
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
            const response = await fetch(`${baseUrl}/explain`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    lean_error: result.lean_proof || result.logs?.join("\n") || "",
                    python_code: result.original_code,
                    filename: result.filename
                })
            });
            const data = await response.json();
            setAiExplanation(data.explanation);
        } catch (error) {
            setAiExplanation("Failed to get explanation. Please try again.");
        } finally {
            setIsExplaining(false);
        }
    };

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden transition-all duration-300 hover:border-gray-700">
            <div
                className="p-4 flex items-center justify-between cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center space-x-4">
                    <FileCode className={`w-6 h-6 ${isSecure ? 'text-green-400' : isPatched ? 'text-yellow-400' : 'text-red-400'}`} />
                    <h3 className="text-lg font-bold text-gray-200">{result.filename}</h3>
                </div>

                <div className="flex items-center space-x-4">
                    {getStatusBadge()}
                    {expanded ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                </div>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-gray-800"
                    >
                        {/* Vulnerability Explanation Section (NEW) */}
                        {isVulnerable && (
                            <div className="p-4 bg-red-950/30 border-b border-red-900/50">
                                <div className="flex items-center justify-between mb-3">
                                    <h4 className="text-sm font-bold text-red-400 flex items-center gap-2">
                                        <span>⚠️</span> WHY IS THIS VULNERABLE?
                                    </h4>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); askGemini(); }}
                                        disabled={isExplaining}
                                        className="flex items-center gap-2 px-3 py-1.5 bg-purple-600/80 hover:bg-purple-500 rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
                                    >
                                        {isExplaining ? (
                                            <><Loader2 className="w-3 h-3 animate-spin" /> Thinking...</>
                                        ) : (
                                            <><Lightbulb className="w-3 h-3" /> Ask Gemini</>
                                        )}
                                    </button>
                                </div>

                                {/* Static Explanation from Report */}
                                {result.error_explanation && (
                                    <p className="text-sm text-gray-300 mb-3">{result.error_explanation}</p>
                                )}

                                {/* Counterexample Table */}
                                {result.counterexample && Object.keys(result.counterexample).length > 0 && (
                                    <div className="mt-3">
                                        <p className="text-xs text-gray-400 mb-2 font-bold">COUNTEREXAMPLE:</p>
                                        <div className="grid grid-cols-3 gap-2">
                                            {Object.entries(result.counterexample).map(([key, value]) => (
                                                <div key={key} className="bg-black/50 rounded p-2 text-center">
                                                    <div className="text-xs text-gray-500">{key}</div>
                                                    <div className="text-lg font-bold text-white">{String(value)}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* AI-Generated Explanation */}
                                {aiExplanation && (
                                    <div className="mt-4 p-3 bg-purple-900/30 border border-purple-800/50 rounded-lg">
                                        <p className="text-xs text-purple-300 font-bold mb-2">🤖 GEMINI EXPLANATION:</p>
                                        <p className="text-sm text-gray-200 whitespace-pre-wrap">{aiExplanation}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Code Comparison */}
                        <div className="grid grid-cols-2 gap-4 p-4 h-96">
                            <CodeEditor
                                label="ORIGINAL [PYTHON]"
                                value={result.original_code}
                                readOnly={true}
                            />
                            <CodeEditor
                                label={isSecure ? "VERIFIED CODE" : isPatched ? "VERIFIED FIX" : "FAILED FIX ATTEMPT"}
                                value={isSecure ? result.original_code : result.fixed_code}
                                readOnly={true}
                            />
                        </div>

                        {/* Lean Proof Viewer */}
                        {result.lean_proof && (
                            <div className="px-4 pb-4">
                                <ProofViewer
                                    leanCode={result.lean_proof}
                                    title="Formal Verification Proof"
                                    defaultExpanded={false}
                                />
                            </div>
                        )}

                        {/* Audit Logs */}
                        <div className="p-4 bg-black/50 border-t border-gray-800 text-xs text-gray-400 font-mono">
                            <p className="mb-2 font-bold text-gray-300">AUDIT LOGS:</p>
                            {result.logs?.slice(-5).map((log: string, i: number) => (
                                <div key={i}>&gt; {log}</div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
