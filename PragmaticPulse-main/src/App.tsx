/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Shield, AlertTriangle, CheckCircle, RefreshCw, Terminal, ArrowRight, Lock, Smartphone, Mail, Cloud, Info } from 'lucide-react';
import { getResilienceAdvice } from './services/geminiService';

type Scenario = {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
  questions: { id: string; text: string; options: string[] }[];
};

const SCENARIOS: Scenario[] = [
  {
    id: 'lost-phone',
    title: 'Total Phone Loss',
    icon: <Smartphone className="w-6 h-6" />,
    description: 'You lose your primary device. It has your 2FA apps, banking, and primary communication.',
    questions: [
      { id: '2fa', text: 'How do you access 2FA codes without your phone?', options: ['Backup codes printed', 'Cloud sync (Authy/Google)', 'I don\'t have a backup', 'SMS (risky)'] },
      { id: 'find-my', text: 'Is "Find My" or "Find My Device" enabled?', options: ['Yes, and I know the login', 'Yes, but I need 2FA to log in', 'No', 'Unsure'] },
      { id: 'backup', text: 'When was your last full device backup?', options: ['Within 24 hours', 'Weekly', 'Monthly', 'Never'] }
    ]
  },
  {
    id: 'email-breach',
    title: 'Primary Email Breach',
    icon: <Mail className="w-6 h-6" />,
    description: 'Your primary email account is compromised. This is the "master key" to your digital identity.',
    questions: [
      { id: 'password', text: 'Is your email password unique and managed?', options: ['Yes, in a password manager', 'Unique but memorized', 'Reused across sites', 'Simple/Common'] },
      { id: 'recovery', text: 'Is your recovery email/phone up to date?', options: ['Yes, and verified', 'Yes, but old', 'No recovery set', 'Unsure'] },
      { id: '2fa-type', text: 'What 2FA method is on your email?', options: ['Hardware Key (YubiKey)', 'App (TOTP)', 'SMS', 'None'] }
    ]
  },
  {
    id: 'cloud-failure',
    title: 'Cloud Storage Wipe',
    icon: <Cloud className="w-6 h-6" />,
    description: 'Your primary cloud provider (Google Photos, iCloud, OneDrive) accidentally wipes your data.',
    questions: [
      { id: 'local-copy', text: 'Do you have a local physical backup?', options: ['Yes, automated daily', 'Yes, manual monthly', 'No, cloud only', 'I have a second cloud'] },
      { id: 'offline', text: 'Can you access critical docs offline?', options: ['Yes, synced locally', 'Some, but not all', 'No, requires internet', 'Unsure'] },
      { id: 'export', text: 'Have you ever used "Google Takeout" or similar?', options: ['Yes, recently', 'Once, long ago', 'No', 'What is that?'] }
    ]
  }
];

export default function App() {
  const [step, setStep] = useState<'intro' | 'scenario' | 'audit' | 'result'>('intro');
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [loading, setLoading] = useState(false);
  const [advice, setAdvice] = useState<any>(null);
  const [history, setHistory] = useState<{ date: string; score: number; scenario: string }[]>([]);

  useEffect(() => {
    const savedHistory = localStorage.getItem('pragmatic_pulse_history');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const saveToHistory = (score: number, scenario: string) => {
    const newEntry = { date: new Date().toISOString(), score, scenario };
    const updatedHistory = [newEntry, ...history].slice(0, 5);
    setHistory(updatedHistory);
    localStorage.setItem('pragmatic_pulse_history', JSON.stringify(updatedHistory));
  };

  const downloadJSON = () => {
    if (!advice || !selectedScenario) return;
    const report = {
      timestamp: new Date().toISOString(),
      scenario: selectedScenario.title,
      answers,
      audit: advice
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resilience-report-${selectedScenario.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const startScenario = (scenario: Scenario) => {
    setSelectedScenario(scenario);
    setAnswers({});
    setCurrentQuestionIdx(0);
    setStep('audit');
  };

  const handleAnswer = (answer: string) => {
    if (!selectedScenario) return;
    const question = selectedScenario.questions[currentQuestionIdx];
    const newAnswers = { ...answers, [question.text]: answer };
    setAnswers(newAnswers);

    if (currentQuestionIdx < selectedScenario.questions.length - 1) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
    } else {
      generateResult(newAnswers);
    }
  };

  const generateResult = async (finalAnswers: Record<string, string>) => {
    setLoading(true);
    setStep('result');
    const result = await getResilienceAdvice(selectedScenario?.title || '', finalAnswers);
    if (result && result.score !== undefined) {
      saveToHistory(result.score, selectedScenario?.title || '');
    }
    setAdvice(result);
    setLoading(false);
  };

  const reset = () => {
    setStep('intro');
    setSelectedScenario(null);
    setAnswers({});
    setAdvice(null);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-line p-6 flex justify-between items-center bg-bg sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Terminal className="w-6 h-6 text-accent" />
          <h1 className="font-mono font-bold text-xl tracking-tighter uppercase">Pragmatic Pulse</h1>
        </div>
        <div className="text-[10px] font-mono opacity-50 uppercase tracking-widest hidden sm:block">
          System Status: Operational // v1.0.4
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-12">
        <AnimatePresence mode="wait">
          {step === 'intro' && (
            <motion.div
              key="intro"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <h2 className="text-6xl md:text-8xl font-bold tracking-tighter leading-none">
                  ARE YOU <span className="text-accent italic">RESILIENT?</span>
                </h2>
                <p className="text-xl opacity-70 max-w-2xl">
                  Most people assume their digital life is safe until it isn't. 
                  Pragmatic Pulse simulates digital disasters to find your breaking point.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {SCENARIOS.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => startScenario(s)}
                    className="group p-6 border border-line text-left hover:bg-ink hover:text-bg transition-all duration-300 flex flex-col justify-between h-48"
                  >
                    <div>
                      <div className="mb-4 group-hover:text-accent transition-colors">{s.icon}</div>
                      <h3 className="font-bold uppercase tracking-tight text-lg">{s.title}</h3>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono uppercase opacity-50 group-hover:opacity-100">Initialize Simulation</span>
                      <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                    </div>
                  </button>
                ))}
              </div>

              {history.length > 0 && (
                <div className="pt-12 space-y-4">
                  <h3 className="col-header">Local Audit History</h3>
                  <div className="border border-line divide-y divide-line">
                    {history.map((entry, i) => (
                      <div key={i} className="p-4 flex justify-between items-center font-mono text-xs">
                        <div className="flex gap-4">
                          <span className="opacity-50">{new Date(entry.date).toLocaleDateString()}</span>
                          <span className="font-bold uppercase">{entry.scenario}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="opacity-50">SCORE:</span>
                          <span className={entry.score > 70 ? 'text-green-600' : entry.score > 40 ? 'text-accent' : 'text-red-600'}>
                            {entry.score}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-12 border-t border-line/20 flex items-start gap-4 text-xs opacity-50">
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <p>
                  This tool uses technical audit patterns to assess digital risk. 
                  No personal data is stored. All analysis is performed in-session.
                </p>
              </div>
            </motion.div>
          )}

          {step === 'audit' && selectedScenario && (
            <motion.div
              key="audit"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-12"
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-ink text-bg rounded-none">
                  {selectedScenario.icon}
                </div>
                <div>
                  <h2 className="font-bold uppercase tracking-tight text-2xl">{selectedScenario.title}</h2>
                  <p className="text-sm opacity-60">Question {currentQuestionIdx + 1} of {selectedScenario.questions.length}</p>
                </div>
              </div>

              <div className="space-y-8">
                <h3 className="text-3xl md:text-4xl font-medium tracking-tight">
                  {selectedScenario.questions[currentQuestionIdx].text}
                </h3>
                <div className="grid grid-cols-1 gap-3">
                  {selectedScenario.questions[currentQuestionIdx].options.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => handleAnswer(opt)}
                      className="p-5 border border-line text-left hover:border-accent hover:bg-accent/5 transition-all flex justify-between items-center group"
                    >
                      <span className="font-medium">{opt}</span>
                      <div className="w-6 h-6 border border-line rounded-full flex items-center justify-center group-hover:border-accent">
                        <div className="w-2 h-2 bg-accent scale-0 group-hover:scale-100 transition-transform rounded-full" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="w-full bg-line/10 h-1">
                <motion.div 
                  className="bg-accent h-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${((currentQuestionIdx) / selectedScenario.questions.length) * 100}%` }}
                />
              </div>
            </motion.div>
          )}

          {step === 'result' && (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-8"
            >
              {loading ? (
                <div className="flex flex-col items-center justify-center py-24 space-y-6">
                  <RefreshCw className="w-12 h-12 text-accent animate-spin" />
                  <div className="text-center space-y-2">
                    <p className="font-mono text-sm uppercase tracking-widest animate-pulse">Analyzing Vulnerabilities...</p>
                    <p className="text-xs opacity-50">Consulting the Pragmatic Sysadmin Knowledge Base</p>
                  </div>
                </div>
              ) : advice ? (
                <div className="space-y-12">
                  <div className="flex flex-col md:flex-row gap-8 items-start md:items-center justify-between border-b border-line pb-8">
                    <div className="space-y-2">
                      <h2 className="text-5xl font-bold tracking-tighter uppercase">Audit <span className="text-accent">Complete</span></h2>
                      <p className="opacity-60 font-mono text-xs uppercase tracking-widest">Scenario: {selectedScenario?.title}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-[10px] font-mono uppercase opacity-50">Resilience Score</p>
                        <p className="text-6xl font-bold tracking-tighter text-accent">{advice.score}<span className="text-2xl opacity-30">/100</span></p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-6">
                      <div className="space-y-2">
                        <h3 className="col-header">Critical Assessment</h3>
                        <p className="text-lg leading-relaxed">{advice.assessment}</p>
                      </div>
                      
                      <div className="p-6 bg-ink text-bg space-y-4">
                        <div className="flex items-center gap-2 text-accent">
                          <AlertTriangle className="w-5 h-5" />
                          <h3 className="font-bold uppercase text-xs tracking-widest">Single Point of Failure</h3>
                        </div>
                        <p className="font-mono text-sm">{advice.failurePoint}</p>
                      </div>
                    </div>

                      <div className="space-y-6">
                      <h3 className="col-header">Pragmatic Action Plan</h3>
                      <div className="space-y-4">
                        {advice.steps.map((step: string, i: number) => (
                          <div key={i} className="flex gap-4 p-4 border border-line/20 hover:border-accent transition-colors">
                            <div className="font-mono text-accent font-bold">0{i + 1}</div>
                            <p className="text-sm">{step}</p>
                          </div>
                        ))}
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <button 
                          onClick={downloadJSON}
                          className="py-4 border border-line font-bold uppercase tracking-widest text-[10px] hover:bg-ink hover:text-bg transition-colors flex items-center justify-center gap-2"
                        >
                          <Lock className="w-3 h-3" />
                          Export JSON
                        </button>
                        <button 
                          onClick={reset}
                          className="py-4 bg-ink text-bg font-bold uppercase tracking-widest text-[10px] hover:bg-accent transition-colors flex items-center justify-center gap-2"
                        >
                          <RefreshCw className="w-3 h-3" />
                          New Audit
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-24 space-y-6">
                  <AlertTriangle className="w-12 h-12 text-accent mx-auto" />
                  <p>Analysis failed. The system encountered an unexpected error.</p>
                  <button onClick={reset} className="underline font-mono text-sm">Return to Base</button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-line p-6 bg-bg">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[10px] font-mono opacity-50 uppercase tracking-widest">
            &copy; 2026 PragmaticSysadmin.tech // Resilience is not a state, it's a practice.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-[10px] font-mono opacity-50 hover:opacity-100 uppercase tracking-widest transition-opacity">Documentation</a>
            <a href="#" className="text-[10px] font-mono opacity-50 hover:opacity-100 uppercase tracking-widest transition-opacity">Security Policy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
