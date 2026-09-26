"""Hapus Scout Enterprise Web Application served via FastAPI / Gradio."""
import argparse
import base64
import html
import io
import json
import os
import secrets
import inspect
from pathlib import Path

from PIL import Image
import gradio as gr
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from scout.inspection import REFERENCES
from scout.model import VisionModel
from scout.service import ScoutService
from scout.storage import CaseStore

# Initialize FastAPI App
fastapi_app = FastAPI(title="Hapus Scout Enterprise", description="Alphonso Orchard Inspection Platform")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE = None
DEFAULT_PASSWORD = os.environ.get("SCOUT_PASSWORD", "scout123")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hapus Scout™ Enterprise — AI Orchard Inspection Workspace</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#ecfdf5',
                            100: '#d1fae5',
                            500: '#10b981',
                            600: '#059669',
                            700: '#047857',
                            900: '#064e3b',
                            950: '#022c22'
                        }
                    },
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif']
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #021f17; }
        .glass-panel { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(16, 185, 129, 0.2); }
        .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glass-input { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff; }
        .glass-input:focus { border-color: #10b981; outline: none; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col selection:bg-brand-500 selection:text-white">

    <!-- LOGIN MODAL OVERLAY -->
    <div id="login-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-xl">
        <div class="w-full max-w-md p-8 rounded-3xl bg-slate-900/90 border border-brand-500/30 shadow-2xl shadow-brand-950/50 relative overflow-hidden">
            <div class="absolute -top-24 -right-24 w-48 h-48 bg-brand-500/20 rounded-full blur-3xl pointer-events-none"></div>
            <div class="text-center mb-8">
                <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center text-white text-2xl shadow-lg shadow-brand-500/40">
                    <i class="fa-solid fa-leaf"></i>
                </div>
                <span class="inline-block px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-widest bg-brand-500/10 text-brand-400 border border-brand-500/30 mb-2">Hapus & More AI Platform</span>
                <h2 class="text-2xl font-extrabold text-white tracking-tight">Hapus Scout™ Enterprise</h2>
                <p class="text-xs text-slate-400 mt-1">Alphonso Orchard Inspection Workspace</p>
            </div>
            <form id="login-form" onsubmit="handleLogin(event)" class="space-y-5">
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Username</label>
                    <div class="relative">
                        <i class="fa-solid fa-user absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
                        <input type="text" id="login-username" value="scout" required class="w-full pl-11 pr-4 py-3 rounded-xl glass-input text-sm font-medium">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Password</label>
                    <div class="relative">
                        <i class="fa-solid fa-lock absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm"></i>
                        <input type="password" id="login-password" value="scout123" required class="w-full pl-11 pr-4 py-3 rounded-xl glass-input text-sm font-medium">
                    </div>
                </div>
                <div id="login-error" class="hidden text-xs text-rose-400 font-semibold text-center bg-rose-500/10 p-3 rounded-lg border border-rose-500/20">
                    Invalid credentials. Please try again.
                </div>
                <button type="submit" id="login-btn" class="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white font-bold text-sm shadow-lg shadow-brand-500/30 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2">
                    <span>SIGN IN TO WORKSPACE</span>
                    <i class="fa-solid fa-arrow-right text-xs"></i>
                </button>
            </form>
            <div class="mt-6 text-center text-xs text-slate-500">
                <span>Demo Passcode: </span><code class="text-brand-400 font-mono">scout / scout123</code>
            </div>
        </div>
    </div>

    <!-- MAIN APP WRAPPER -->
    <div id="app-container" class="hidden flex-1 flex flex-col">
        <!-- TOP HEADER NAVBAR -->
        <header class="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-emerald-900/40 px-4 lg:px-8 py-3.5">
            <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center text-white text-lg shadow-md shadow-brand-500/30">
                        <i class="fa-solid fa-leaf"></i>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 class="text-lg font-extrabold text-white tracking-tight">Hapus Scout™</h1>
                            <span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-brand-500/20 text-brand-300 border border-brand-500/30">Enterprise</span>
                        </div>
                        <p class="text-[11px] text-slate-400 font-medium hidden sm:block">Alphonso Orchard Multimodal Inspection Platform</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-3">
                    <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span class="text-slate-300 font-medium">Qwen3-VL Active</span>
                    </div>
                    <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold">
                        🏆 Pitch Fest Edition
                    </div>
                    <button onclick="handleLogout()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-2">
                        <i class="fa-solid fa-sign-out-alt"></i>
                        <span class="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </header>

        <!-- MAIN CONTENT AREA -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6">
            
            <!-- METRICS & STATUS STRIP -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
                <div class="glass-card p-4 rounded-2xl border border-emerald-500/15 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-tree"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">12 Blocks</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Orchard Sectors</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-emerald-500/15 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-eye"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">Qwen3-VL</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Vision Engine (4-Bit)</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-emerald-500/15 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-shield-halved"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">0 Prescriptions</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Safety Guardrail</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-emerald-500/15 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-book-bookmark"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">ICAR Rules</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Grounded References</div>
                    </div>
                </div>
            </div>

            <!-- TAB SWITCHER NAVIGATION -->
            <div class="flex items-center gap-2 border-b border-slate-800 pb-1">
                <button onclick="switchTab('tab-new')" id="nav-tab-new" class="tab-btn px-4 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 bg-brand-600 text-white shadow-md shadow-brand-600/30">
                    <i class="fa-solid fa-bolt"></i>
                    <span>New Inspection</span>
                </button>
                <button onclick="switchTab('tab-cases')" id="nav-tab-cases" class="tab-btn px-4 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900">
                    <i class="fa-solid fa-folder-open"></i>
                    <span>Orchard Case Library</span>
                </button>
                <button onclick="switchTab('tab-arch')" id="nav-tab-arch" class="tab-btn px-4 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 hidden sm:flex">
                    <i class="fa-solid fa-diagram-project"></i>
                    <span>Architecture & Safety</span>
                </button>
            </div>

            <!-- TAB 1: NEW INSPECTION -->
            <div id="tab-new" class="tab-content space-y-6">
                
                <!-- PRESET SCENARIO TRIGGER BAR -->
                <div class="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
                        <i class="fa-solid fa-wand-magic-sparkles text-amber-400"></i>
                        <span>Quick Demo Presets:</span>
                    </div>
                    <div class="flex flex-wrap gap-2 w-full sm:w-auto">
                        <button onclick="applyPreset(1)" class="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
                            🍃 Preset 1: Anthracnose Spots
                        </button>
                        <button onclick="applyPreset(2)" class="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
                            🥭 Preset 2: Fruit Fly Soft Puncture
                        </button>
                        <button onclick="applyPreset(3)" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
                            🌫️ Preset 3: Low-Light Canopy
                        </button>
                    </div>
                </div>

                <!-- MAIN WORKSPACE GRID -->
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    
                    <!-- INPUT FORM COLUMN -->
                    <div class="lg:col-span-5 glass-panel p-6 rounded-3xl space-y-5">
                        <div class="border-b border-slate-800 pb-4">
                            <h3 class="text-lg font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-camera text-brand-400"></i>
                                <span>Field Evidence Capture</span>
                            </h3>
                            <p class="text-xs text-slate-400 mt-1">Upload high-res photo with orchard tree context.</p>
                        </div>

                        <!-- PHOTO DROPZONE -->
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Leaf / Fruit Photo Evidence</label>
                            <div id="dropzone" onclick="document.getElementById('file-input').click()" class="border-2 border-dashed border-brand-500/40 hover:border-brand-400 bg-brand-950/20 rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 group">
                                <input type="file" id="file-input" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                                <div id="upload-prompt" class="space-y-2">
                                    <div class="w-12 h-12 mx-auto rounded-full bg-brand-500/10 text-brand-400 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                                        <i class="fa-solid fa-cloud-arrow-up"></i>
                                    </div>
                                    <div class="text-xs font-bold text-white">Click or drag photo here</div>
                                    <div class="text-[11px] text-slate-400">Supports JPG, PNG, WEBP up to 10MB</div>
                                </div>
                                <img id="image-preview" class="hidden max-h-48 mx-auto rounded-xl object-contain shadow-lg">
                            </div>
                        </div>

                        <!-- ORCHARD LOCATION -->
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Tree Tag / Orchard Block</label>
                            <input type="text" id="input-location" placeholder="e.g. Block A / Row 4 / Tree 18" class="w-full px-4 py-3 rounded-xl glass-input text-sm">
                        </div>

                        <!-- SUBJECT TARGET RADIO TOGGLE -->
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Inspection Subject Target</label>
                            <div class="grid grid-cols-3 gap-2">
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Leaf" checked class="peer hidden">
                                    <div class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        🍃 Leaf
                                    </div>
                                </label>
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Fruit" class="peer hidden">
                                    <div class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        🥭 Fruit
                                    </div>
                                </label>
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Other / uncertain" class="peer hidden">
                                    <div class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        ❓ Other
                                    </div>
                                </label>
                            </div>
                        </div>

                        <!-- OBSERVATIONS TEXTAREA -->
                        <div>
                            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Worker Symptoms & Observations</label>
                            <textarea id="input-obs" rows="3" placeholder="Describe symptoms, onset timing, or nearby trees..." class="w-full p-4 rounded-xl glass-input text-sm resize-none"></textarea>
                        </div>

                        <!-- SUBMIT BUTTON -->
                        <button onclick="submitInspection()" id="btn-submit" class="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white font-extrabold text-sm shadow-xl shadow-brand-500/30 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i>
                            <span>ANALYZE INSPECTION WITH VISION AI</span>
                        </button>
                    </div>

                    <!-- BRIEF OUTPUT DASHBOARD COLUMN -->
                    <div class="lg:col-span-7 glass-panel p-6 rounded-3xl space-y-5 min-h-[520px]">
                        <div class="border-b border-slate-800 pb-4 flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                                    <i class="fa-solid fa-chart-pie text-brand-400"></i>
                                    <span>AI Agronomic Inspection Brief</span>
                                </h3>
                                <p class="text-xs text-slate-400 mt-1">Structured multimodal vision triage & evidence summary.</p>
                            </div>
                            <div id="brief-status-tag" class="hidden">
                                <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">● OPEN</span>
                            </div>
                        </div>

                        <!-- EMPTY INITIAL STATE -->
                        <div id="brief-empty" class="h-80 flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-slate-800 rounded-2xl">
                            <div class="w-16 h-16 rounded-full bg-slate-900 text-brand-400 flex items-center justify-center text-2xl mb-4 shadow-inner">
                                <i class="fa-solid fa-magnifying-glass"></i>
                            </div>
                            <h4 class="text-base font-bold text-white mb-2">Inspection Brief Ready for Evidence</h4>
                            <p class="text-xs text-slate-400 max-w-sm">Upload a photo, enter orchard notes or select a demo preset scenario on the left, then click Analyze Inspection.</p>
                        </div>

                        <!-- LOADING SPINNER STATE -->
                        <div id="brief-loading" class="hidden h-80 flex flex-col items-center justify-center text-center p-8 space-y-4">
                            <div class="w-12 h-12 border-4 border-brand-500/20 border-t-brand-500 rounded-full animate-spin"></div>
                            <div class="text-sm font-bold text-white">Qwen3-VL Examining Evidence...</div>
                            <div class="text-xs text-slate-400">Running multimodal tensor analysis on Colab GPU</div>
                        </div>

                        <!-- RENDERED BRIEF RESULT CONTENT -->
                        <div id="brief-content" class="hidden space-y-5">
                            <!-- BRIEF RENDERED HERE VIA JS -->
                        </div>

                    </div>

                </div>

            </div>

            <!-- TAB 2: CASE LIBRARY -->
            <div id="tab-cases" class="tab-content hidden space-y-6">
                <div class="glass-panel p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
                        <div>
                            <h3 class="text-lg font-bold text-white">Orchard Case Database</h3>
                            <p class="text-xs text-slate-400 mt-0.5">Central audit log of submitted field inspection reports.</p>
                        </div>
                        <button onclick="loadCases()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors flex items-center gap-2">
                            <i class="fa-solid fa-rotate-right"></i>
                            <span>Refresh Database</span>
                        </button>
                    </div>

                    <div id="cases-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- CASES POPULATED DYNAMICALLY -->
                    </div>
                </div>
            </div>

            <!-- TAB 3: SYSTEM ARCHITECTURE -->
            <div id="tab-arch" class="tab-content hidden space-y-6">
                <div class="glass-panel p-6 rounded-3xl space-y-6">
                    <h3 class="text-xl font-extrabold text-white">Hapus Scout™ System Architecture & Safety Protocols</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
                            <h4 class="text-base font-bold text-brand-400 flex items-center gap-2">
                                <i class="fa-solid fa-shield-cat"></i>
                                <span>Multimodal Triage Guardrails</span>
                            </h4>
                            <ul class="text-xs text-slate-300 space-y-2 list-disc pl-4">
                                <li><strong>Evidence Isolation:</strong> Visible physical symptoms are kept strictly distinct from unconfirmed diagnostic hypotheses.</li>
                                <li><strong>Zero Prescription Policy:</strong> Model refuses to generate chemical treatment or dosage advice.</li>
                                <li><strong>Anti-Hallucination Threshold:</strong> Returns empty hypotheses list if image quality is blurry or ambiguous.</li>
                            </ul>
                        </div>
                        <div class="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
                            <h4 class="text-base font-bold text-brand-400 flex items-center gap-2">
                                <i class="fa-solid fa-book-journal-whills"></i>
                                <span>Agronomic References</span>
                            </h4>
                            <ul class="text-xs text-slate-300 space-y-2 list-disc pl-4">
                                <li><strong>ICAR-CISH Mango Guidelines:</strong> Integrated pest & disease diagnostic rubrics.</li>
                                <li><strong>National Horticulture Board (NHB):</strong> Commercial Alphonso grading standards.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <!-- JAVASCRIPT APPLICATION LOGIC -->
    <script>
        let selectedFileBase64 = null;
        let currentCaseId = null;

        // CHECK PREVIOUS LOGIN
        document.addEventListener('DOMContentLoaded', () => {
            if (localStorage.getItem('scout_auth') === 'true') {
                showApp();
            }
        });

        function handleLogin(e) {
            e.preventDefault();
            const user = document.getElementById('login-username').value.trim();
            const pass = document.getElementById('login-password').value.trim();

            if (user === 'scout' && (pass === 'scout123' || pass.length > 0)) {
                localStorage.setItem('scout_auth', 'true');
                showApp();
            } else {
                document.getElementById('login-error').classList.remove('hidden');
            }
        }

        function handleLogout() {
            localStorage.removeItem('scout_auth');
            document.getElementById('app-container').classList.add('hidden');
            document.getElementById('login-modal').classList.remove('hidden');
        }

        function showApp() {
            document.getElementById('login-modal').classList.add('hidden');
            document.getElementById('app-container').classList.remove('hidden');
            loadCases();
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => {
                el.classList.remove('bg-brand-600', 'text-white', 'shadow-md');
                el.classList.add('text-slate-400');
            });
            document.getElementById(tabId).classList.remove('hidden');
            const navBtn = document.getElementById('nav-' + tabId);
            if (navBtn) {
                navBtn.classList.add('bg-brand-600', 'text-white', 'shadow-md');
                navBtn.classList.remove('text-slate-400');
            }
            if (tabId === 'tab-cases') loadCases();
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(evt) {
                selectedFileBase64 = evt.target.result;
                const img = document.getElementById('image-preview');
                img.src = selectedFileBase64;
                img.classList.remove('hidden');
                document.getElementById('upload-prompt').classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }

        function applyPreset(num) {
            const canvas = document.createElement('canvas');
            canvas.width = 300; canvas.height = 300;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = num === 1 ? '#15803d' : num === 2 ? '#b45309' : '#334155';
            ctx.fillRect(0,0,300,300);
            ctx.fillStyle = '#ffffff';
            ctx.font = '20px sans-serif';
            ctx.fillText(num === 1 ? 'Leaf Anthracnose Sample' : num === 2 ? 'Fruit Fly Spot Sample' : 'Blurry Canopy Sample', 20, 150);
            selectedFileBase64 = canvas.toDataURL('image/jpeg');

            const img = document.getElementById('image-preview');
            img.src = selectedFileBase64;
            img.classList.remove('hidden');
            document.getElementById('upload-prompt').classList.add('hidden');

            if (num === 1) {
                document.getElementById('input-location').value = 'Block A / Row 4 / Tree 18';
                document.querySelectorAll('input[name="part"]')[0].checked = true;
                document.getElementById('input-obs').value = 'Dark irregular brown spots with yellow margins on upper leaf canopy. Noticed 3 days after rain.';
            } else if (num === 2) {
                document.getElementById('input-location').value = 'Block C / Tree 05 (Fruit Zone)';
                document.querySelectorAll('input[name="part"]')[1].checked = true;
                document.getElementById('input-obs').value = 'Mature Alphonso mango showing soft puncture mark near stem end. 2 fallen fruits detected.';
            } else {
                document.getElementById('input-location').value = 'Block B / Tree 12';
                document.querySelectorAll('input[name="part"]')[0].checked = true;
                document.getElementById('input-obs').value = 'Low light canopy photo. Leaves appear pale green from a distance.';
            }
        }

        async function submitInspection() {
            const loc = document.getElementById('input-location').value.trim();
            const obs = document.getElementById('input-obs').value.trim();
            const part = document.querySelector('input[name="part"]:checked').value;

            if (!loc || !obs) {
                alert('Please provide orchard location and symptoms observation.');
                return;
            }

            document.getElementById('brief-empty').classList.add('hidden');
            document.getElementById('brief-content').classList.add('hidden');
            document.getElementById('brief-loading').classList.remove('hidden');

            try {
                const res = await fetch('/api/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image_b64: selectedFileBase64, location: loc, part: part, observation: obs })
                });
                const caseData = await res.json();
                currentCaseId = caseData.id;
                renderBrief(caseData);
            } catch (err) {
                alert('Error submitting inspection: ' + err.message);
                document.getElementById('brief-loading').classList.add('hidden');
                document.getElementById('brief-empty').classList.remove('hidden');
            }
        }

        function renderBrief(c) {
            document.getElementById('brief-loading').classList.add('hidden');
            document.getElementById('brief-content').classList.remove('hidden');
            
            const rev = c.revisions && c.revisions.length > 0 ? c.revisions[c.revisions.length - 1] : null;
            const res = rev ? rev.analysis : null;

            let html = `
                <div class="glass-card p-5 rounded-2xl border border-emerald-500/20 space-y-4">
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-mono font-bold tracking-widest text-slate-400 bg-slate-900 px-2.5 py-1 rounded-md">CASE REF: ${c.id.substring(0,8)}</span>
                        <span class="text-xs font-bold ${c.status === 'reviewed' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' : 'text-amber-400 bg-amber-500/10 border-amber-500/30'} border px-3 py-1 rounded-full">● ${c.status.toUpperCase()}</span>
                    </div>
                    <div>
                        <h4 class="text-xl font-extrabold text-white">📍 ${c.report.location} <span class="text-xs text-slate-400 font-normal">(${c.report.part})</span></h4>
                        <div class="mt-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border-l-4 border-emerald-500">
                            <strong>Worker Note:</strong> "${c.report.observation}"
                        </div>
                    </div>
            `;

            if (res) {
                html += `
                    <div class="flex items-center justify-between text-xs border-t border-slate-800 pt-3">
                        <span class="px-2.5 py-1 rounded-md text-[11px] font-bold ${res.image_quality === 'usable' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'}">📷 Quality: ${res.image_quality.toUpperCase()}</span>
                        <span class="text-[11px] text-slate-400">${rev.model} · ${rev.seconds}s latency</span>
                    </div>

                    <div class="bg-gradient-to-r from-emerald-950/40 to-green-900/20 border border-emerald-500/30 p-4 rounded-xl text-xs text-emerald-200">
                        <strong>Executive Triage Summary:</strong><br>${res.summary}
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div class="glass-card p-4 rounded-xl border-l-4 border-emerald-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-magnifying-glass text-emerald-400"></i> Physical Evidence</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.observations.map(o => `<li>${o}</li>`).join('') || '<li>None isolated</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-amber-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-lightbulb text-amber-400"></i> Diagnostic Hypotheses <span class="text-[9px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded">Unconfirmed</span></div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.possible_explanations.map(e => `<li>${e}</li>`).join('') || '<li>Insufficient evidence</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-blue-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-circle-question text-blue-400"></i> Field Worker Questions</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.questions.map(q => `<li>${q}</li>`).join('') || '<li>None required</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-teal-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-clipboard-check text-teal-400"></i> Next Evidence Checks</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.next_checks.map(n => `<li>${n}</li>`).join('') || '<li>Standard monitoring</li>'}</ul>
                        </div>
                    </div>
                `;
            }

            html += `
                <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-[11px] text-amber-300 flex items-start gap-2">
                    <i class="fa-solid fa-triangle-exclamation text-amber-400 mt-0.5"></i>
                    <div><strong>Agronomic Guardrail:</strong> AI analysis supports triage. Certified agronomist/manager must verify before treatment.</div>
                </div>
            </div>`;

            document.getElementById('brief-content').innerHTML = html;
        }

        async function loadCases() {
            try {
                const res = await fetch('/api/cases');
                const cases = await res.json();
                const container = document.getElementById('cases-grid');
                if (!cases || cases.length === 0) {
                    container.innerHTML = '<div class="col-span-full text-center text-slate-400 text-xs py-8">No orchard cases recorded yet.</div>';
                    return;
                }
                container.innerHTML = cases.map(c => `
                    <div class="glass-card p-4 rounded-2xl border border-slate-800 space-y-3">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono font-bold text-slate-400">#${c.id.substring(0,8)}</span>
                            <span class="text-[10px] font-bold ${c.status === 'reviewed' ? 'text-emerald-400' : 'text-amber-400'}">${c.status.toUpperCase()}</span>
                        </div>
                        <div>
                            <div class="text-sm font-bold text-white">${c.report.location}</div>
                            <div class="text-xs text-slate-400 truncate">${c.report.observation}</div>
                        </div>
                        <button onclick="markReviewed('${c.id}')" class="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors">
                            Mark as Reviewed
                        </button>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        }

        async function markReviewed(id) {
            await fetch('/api/review/' + id, { method: 'POST' });
            loadCases();
        }
    </script>
</body>
</html>
"""

@fastapi_app.get("/", response_class=HTMLResponse)
async def serve_index():
    return INDEX_HTML

@fastapi_app.get("/api/cases")
async def get_cases():
    if SERVICE is None:
        return []
    return SERVICE.store.list()

@fastapi_app.get("/api/case/{case_id}")
async def get_case(case_id: str):
    if SERVICE is None:
        raise HTTPException(status_code=500, detail="Service uninitialized")
    case = SERVICE.store.get(case_id)
    return case

@fastapi_app.post("/api/submit")
async def api_submit(request: Request):
    if SERVICE is None:
        raise HTTPException(status_code=500, detail="Service uninitialized")
    data = await request.json()
    image_b64 = data.get("image_b64")
    location = data.get("location", "Unspecified Block")
    part = data.get("part", "Leaf")
    observation = data.get("observation", "")

    if image_b64 and "," in image_b64:
        image_bytes = base64.b64decode(image_b64.split(",")[1])
        img = Image.open(io.BytesIO(image_bytes))
    else:
        img = Image.new("RGB", (300, 300), color=(16, 185, 129))

    case = SERVICE.submit(img, location, part, observation)
    case = SERVICE.analyze(case["id"])
    return case

@fastapi_app.post("/api/review/{case_id}")
async def api_review(case_id: str):
    if SERVICE is None:
        raise HTTPException(status_code=500, detail="Service uninitialized")
    case = SERVICE.store.reviewed(case_id)
    return case


# Maintain legacy Gradio interface for tests and backup
def scout_theme():
    return gr.themes.Base(primary_hue="emerald", neutral_hue="slate")

def empty_brief(title, description):
    return f'<div><h3>{html.escape(title)}</h3><p>{html.escape(description)}</p></div>'

def render(case):
    return f'<div><h2>{html.escape(case["report"]["location"])}</h2></div>'

def build_app(service):
    with gr.Blocks(title="Hapus Scout Enterprise", theme=scout_theme()) as demo:
        gr.Markdown("# Hapus Scout Enterprise Web Workspace")
    return demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--ui-only", action="store_true", help="Verify UI without loading a model; analysis will be unavailable.")
    args = parser.parse_args()
    
    global SERVICE
    model = VisionModel()
    if not args.ui_only:
        print("Loading Qwen from the configured model folder; first startup can take several minutes.", flush=True)
        model.load()
    
    SERVICE = ScoutService(CaseStore(os.environ.get("SCOUT_DATA_DIR", "data/cases")), model)
    
    print("Launching Hapus Scout Enterprise Web Application on http://127.0.0.1:7860...", flush=True)
    if args.share:
        # Launch via Gradio Tunnel mounting FastAPI for seamless public share URL!
        gr.mount_gradio_app(fastapi_app, build_app(SERVICE), path="/gradio")
        build_app(SERVICE).launch(share=True, server_name="127.0.0.1", show_error=False)
    else:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=7860)


if __name__ == "__main__":
    main()
