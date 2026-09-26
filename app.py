"""Hapus Scout Enterprise Web Application (Custom Tailwind CSS SPA + FastAPI + Gradio Tunnel)."""
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
from gradio.tunneling import Tunnel
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from scout.inspection import REFERENCES
from scout.model import VisionModel
from scout.service import ScoutService
from scout.storage import CaseStore

# Initialize FastAPI Application
fastapi_app = FastAPI(title="Hapus Scout Enterprise", description="Alphonso Orchard Inspection Platform")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE = None

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
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; }
        .glass-panel { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(30, 41, 59, 0.8); }
        .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glass-input { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.15); color: #ffffff; }
        .glass-input:focus { border-color: #10b981; outline: none; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
        @keyframes laser-scan {
            0% { top: 0%; opacity: 0.2; }
            50% { opacity: 1.0; }
            100% { top: 92%; opacity: 0.2; }
        }
        .animate-laser-scan {
            animation: laser-scan 2.2s ease-in-out infinite alternate;
        }
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col selection:bg-brand-500 selection:text-white bg-slate-950">

    <!-- LOGIN MODAL OVERLAY -->
    <div id="login-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/95 backdrop-blur-2xl">
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
        <header class="sticky top-0 z-40 bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/80 px-4 lg:px-8 py-3.5">
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
                        <p data-i18n="app_sub" class="text-[11px] text-slate-400 font-medium hidden sm:block">Alphonso Orchard Multimodal Inspection Platform</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-3">
                    <!-- MULTILINGUAL LANGUAGE SELECTOR -->
                    <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-emerald-500/40 text-xs shadow-md shadow-emerald-500/10">
                        <i class="fa-solid fa-globe text-emerald-400"></i>
                        <select id="lang-select" onchange="changeLanguage(this.value)" class="bg-transparent text-slate-200 text-xs font-extrabold focus:outline-none cursor-pointer">
                            <option value="en" class="bg-slate-900 text-white">English (EN)</option>
                            <option value="mr" class="bg-slate-900 text-white">मराठी (MR)</option>
                            <option value="hi" class="bg-slate-900 text-white">हिंदी (HI)</option>
                        </select>
                    </div>

                    <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span class="text-slate-300 font-medium">Qwen3-VL Active</span>
                    </div>
                    <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold">
                        🏆 Pitch Fest Edition
                    </div>
                    <button onclick="handleLogout()" class="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-semibold transition-colors flex items-center gap-2">
                        <i class="fa-solid fa-sign-out-alt"></i>
                        <span data-i18n="logout" class="hidden sm:inline">Logout</span>
                    </button>
                </div>
            </div>
        </header>

        <!-- MAIN CONTENT AREA -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6">
            
            <!-- METRICS & STATUS STRIP -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
                <div class="glass-card p-4 rounded-2xl border border-slate-800 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-tree"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">12 Blocks</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Orchard Sectors</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-slate-800 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-eye"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">Qwen3-VL</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Vision Engine (4-Bit)</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-slate-800 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-lg font-bold">
                        <i class="fa-solid fa-shield-halved"></i>
                    </div>
                    <div>
                        <div class="text-lg font-extrabold text-white">0 Prescriptions</div>
                        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Safety Guardrail</div>
                    </div>
                </div>
                <div class="glass-card p-4 rounded-2xl border border-slate-800 flex items-center gap-3">
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
                    <span data-i18n="nav_new">New Inspection</span>
                </button>
                <button onclick="switchTab('tab-cases')" id="nav-tab-cases" class="tab-btn px-4 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900">
                    <i class="fa-solid fa-folder-open"></i>
                    <span data-i18n="nav_cases">Orchard Case Library</span>
                </button>
                <button onclick="switchTab('tab-arch')" id="nav-tab-arch" class="tab-btn px-4 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center gap-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 hidden sm:flex">
                    <i class="fa-solid fa-diagram-project"></i>
                    <span data-i18n="nav_arch">Architecture & Safety</span>
                </button>
            </div>

            <!-- TAB 1: NEW INSPECTION -->
            <div id="tab-new" class="tab-content space-y-6">
                
                <!-- PRESET SCENARIO TRIGGER BAR -->
                <div class="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
                        <i class="fa-solid fa-wand-magic-sparkles text-amber-400"></i>
                        <span data-i18n="preset_label">Quick Demo Presets:</span>
                    </div>
                    <div class="flex flex-wrap gap-2 w-full sm:w-auto">
                        <button onclick="applyPreset(1)" data-i18n="preset_1" class="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
                            🍃 Preset 1: Anthracnose Spots
                        </button>
                        <button onclick="applyPreset(2)" data-i18n="preset_2" class="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
                            🥭 Preset 2: Fruit Fly Soft Puncture
                        </button>
                        <button onclick="applyPreset(3)" data-i18n="preset_3" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors flex items-center gap-1.5">
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
                                <span data-i18n="field_title">Field Evidence Capture</span>
                            </h3>
                            <p data-i18n="field_sub" class="text-xs text-slate-400 mt-1">Upload high-res photo with orchard tree context.</p>
                        </div>

                        <!-- PHOTO DROPZONE -->
                        <div>
                            <label data-i18n="photo_label" class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Leaf / Fruit Photo Evidence</label>
                            <div id="dropzone" onclick="document.getElementById('file-input').click()" class="border-2 border-dashed border-brand-500/40 hover:border-brand-400 bg-brand-950/20 rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 group">
                                <input type="file" id="file-input" accept="image/*" class="hidden" onchange="handleFileSelect(event)">
                                <div id="upload-prompt" class="space-y-2">
                                    <div class="w-12 h-12 mx-auto rounded-full bg-brand-500/10 text-brand-400 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                                        <i class="fa-solid fa-cloud-arrow-up"></i>
                                    </div>
                                    <div data-i18n="upload_title" class="text-xs font-bold text-white">Click or drag photo here</div>
                                    <div data-i18n="upload_sub" class="text-[11px] text-slate-400">Supports JPG, PNG, WEBP up to 10MB</div>
                                </div>
                                <img id="image-preview" class="hidden max-h-48 mx-auto rounded-xl object-contain shadow-lg">
                            </div>
                        </div>

                        <!-- ORCHARD LOCATION -->
                        <div>
                            <label data-i18n="location_label" class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Tree Tag / Orchard Block</label>
                            <input type="text" id="input-location" data-i18n-placeholder="location_placeholder" placeholder="e.g. Block A / Row 4 / Tree 18" class="w-full px-4 py-3 rounded-xl glass-input text-sm">
                        </div>

                        <!-- SUBJECT TARGET RADIO TOGGLE -->
                        <div>
                            <label data-i18n="subject_label" class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Inspection Subject Target</label>
                            <div class="grid grid-cols-3 gap-2">
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Leaf" checked class="peer hidden">
                                    <div data-i18n="part_leaf" class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        🍃 Leaf
                                    </div>
                                </label>
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Fruit" class="peer hidden">
                                    <div data-i18n="part_fruit" class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        🥭 Fruit
                                    </div>
                                </label>
                                <label class="cursor-pointer">
                                    <input type="radio" name="part" value="Other / uncertain" class="peer hidden">
                                    <div data-i18n="part_other" class="py-2.5 px-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 peer-checked:bg-brand-600 peer-checked:text-white peer-checked:border-brand-500 text-xs font-bold text-center transition-all">
                                        ❓ Other
                                    </div>
                                </label>
                            </div>
                        </div>

                        <!-- OBSERVATIONS TEXTAREA -->
                        <div>
                            <label data-i18n="obs_label" class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Worker Symptoms & Observations</label>
                            <textarea id="input-obs" data-i18n-placeholder="obs_placeholder" rows="3" placeholder="Describe symptoms, onset timing, or nearby trees..." class="w-full p-4 rounded-xl glass-input text-sm resize-none"></textarea>
                        </div>

                        <!-- SUBMIT BUTTON -->
                        <button onclick="submitInspection()" id="btn-submit" class="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white font-extrabold text-sm shadow-xl shadow-brand-500/30 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i>
                            <span data-i18n="submit_btn">ANALYZE INSPECTION WITH VISION AI</span>
                        </button>
                    </div>

                    <!-- BRIEF OUTPUT DASHBOARD COLUMN -->
                    <div class="lg:col-span-7 glass-panel p-6 rounded-3xl space-y-5 min-h-[520px]">
                        <div class="border-b border-slate-800 pb-4 flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                                    <i class="fa-solid fa-chart-pie text-brand-400"></i>
                                    <span data-i18n="brief_title">AI Agronomic Inspection Brief</span>
                                </h3>
                                <p data-i18n="brief_sub" class="text-xs text-slate-400 mt-1">Structured multimodal vision triage & evidence summary.</p>
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
                            <h4 data-i18n="empty_title" class="text-base font-bold text-white mb-2">Inspection Brief Ready for Evidence</h4>
                            <p data-i18n="empty_desc" class="text-xs text-slate-400 max-w-sm">Upload a photo, enter orchard notes or select a demo preset scenario on the left, then click Analyze Inspection.</p>
                        </div>

                        <!-- FUTURISTIC AGRICULTURE VISION AI SCANNER HUD -->
                        <div id="brief-loading" class="hidden min-h-[460px] flex flex-col items-center justify-center p-6 space-y-5">
                            
                            <!-- CYBER SCANNER FRAME WITH SCANNING LASER LINE -->
                            <div class="relative w-72 h-48 rounded-2xl bg-slate-950 border-2 border-emerald-500/40 shadow-2xl shadow-emerald-500/20 overflow-hidden flex items-center justify-center group">
                                <!-- Tech Corner HUD Brackets -->
                                <div class="absolute top-2 left-2 w-3 h-3 border-t-2 border-l-2 border-emerald-400 z-20"></div>
                                <div class="absolute top-2 right-2 w-3 h-3 border-t-2 border-r-2 border-emerald-400 z-20"></div>
                                <div class="absolute bottom-2 left-2 w-3 h-3 border-b-2 border-l-2 border-emerald-400 z-20"></div>
                                <div class="absolute bottom-2 right-2 w-3 h-3 border-b-2 border-r-2 border-emerald-400 z-20"></div>

                                <!-- Scanning Matrix Background Grid -->
                                <div class="absolute inset-0 opacity-20 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:12px_12px] z-0"></div>

                                <!-- Scanning Holographic Image Container -->
                                <img id="loader-scan-img" src="" class="w-full h-full object-cover filter saturate-150 contrast-125 z-10 transition-all duration-300">
                                
                                <!-- Bounding Box Detection Overlay (Futuristic HUD) -->
                                <div id="loader-bounding-box" class="absolute border-2 border-dashed border-emerald-400 bg-emerald-500/20 rounded-md z-20 transition-all duration-500 flex items-start p-1" style="top:20%; left:25%; width:50%; height:55%;">
                                    <span class="text-[9px] font-mono font-bold text-emerald-300 bg-slate-950/80 px-1 rounded shadow border border-emerald-500/30">CONF: 98.4%</span>
                                </div>

                                <!-- Animated Scanning Laser Line -->
                                <div class="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_18px_#10b981] animate-laser-scan z-30"></div>

                                <!-- Live HUD Telemetry Badge Overlay -->
                                <div class="absolute bottom-2 inset-x-2 bg-slate-950/90 border border-emerald-500/40 backdrop-blur-md rounded-lg p-1.5 flex items-center justify-between text-[10px] font-mono text-emerald-300 z-30">
                                    <span class="flex items-center gap-1.5"><i class="fa-solid fa-microchip text-emerald-400 animate-spin"></i> 1024 PATCHES</span>
                                    <span class="text-amber-300 font-bold" id="loader-tensor-latency">142ms/tok</span>
                                </div>
                            </div>

                            <!-- TIMER & DYNAMIC STAGE TITLE -->
                            <div class="text-center space-y-1.5 max-w-md">
                                <div class="flex items-center justify-center gap-2">
                                    <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-mono font-extrabold tracking-widest shadow-sm shadow-emerald-500/30">
                                        ⏱️ <span id="loader-timer">0.0s</span>
                                    </span>
                                    <span class="text-xs text-slate-400 font-mono">EST. ~6.5s INFERENCE</span>
                                </div>
                                <h4 id="loader-stage-title" class="text-base font-extrabold text-white tracking-wide transition-all duration-300">🌱 1. Visual Matrix Scanning</h4>
                                <p id="loader-stage-desc" class="text-xs text-slate-300 transition-all duration-300">Preprocessing canopy photo & segmenting leaf/fruit boundaries...</p>
                            </div>

                            <!-- 4-STEP FUTURISTIC CYBER PIPELINE -->
                            <div class="w-full max-w-md grid grid-cols-4 gap-1.5 pt-1">
                                <div id="loader-step-1" class="py-2 px-1 rounded-lg bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 text-[10px] font-bold text-center shadow-sm shadow-emerald-500/20 transition-all duration-300">
                                    01 SCAN
                                </div>
                                <div id="loader-step-2" class="py-2 px-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-500 text-[10px] font-bold text-center transition-all duration-300">
                                    02 QWEN
                                </div>
                                <div id="loader-step-3" class="py-2 px-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-500 text-[10px] font-bold text-center transition-all duration-300">
                                    03 ICAR
                                </div>
                                <div id="loader-step-4" class="py-2 px-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-500 text-[10px] font-bold text-center transition-all duration-300">
                                    04 BRIEF
                                </div>
                            </div>

                            <!-- REAL-TIME LOG TERMINAL FEED -->
                            <div class="w-full max-w-md p-3 bg-slate-950/90 border border-slate-800 rounded-xl text-left text-[10px] font-mono text-slate-400 space-y-1 overflow-hidden">
                                <div class="text-emerald-400 font-bold flex items-center justify-between border-b border-slate-800 pb-1">
                                    <span><i class="fa-solid fa-terminal"></i> AGRONOMIC TENSOR LOG</span>
                                    <span class="text-[9px] text-slate-500">LIVE FEED</span>
                                </div>
                                <div id="loader-log-feed" class="text-slate-300 truncate">
                                    > Segmenting plant tissue against orchard background...
                                </div>
                            </div>
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
        let currentLang = 'en';

        const I18N_DICT = {
            en: {
                app_sub: "Alphonso Orchard Multimodal Inspection Platform",
                nav_new: "New Inspection",
                nav_cases: "Orchard Case Library",
                nav_arch: "Architecture & Safety",
                preset_label: "Quick Demo Presets:",
                preset_1: "🍃 Preset 1: Anthracnose Spots",
                preset_2: "🥭 Preset 2: Fruit Fly Soft Puncture",
                preset_3: "🌫️ Preset 3: Low-Light Canopy",
                field_title: "Field Evidence Capture",
                field_sub: "Upload high-res photo with orchard tree context.",
                photo_label: "Leaf / Fruit Photo Evidence",
                upload_title: "Click or drag photo here",
                upload_sub: "Supports JPG, PNG, WEBP up to 10MB",
                location_label: "Tree Tag / Orchard Block",
                location_placeholder: "e.g. Block A / Row 4 / Tree 18",
                subject_label: "Inspection Subject Target",
                part_leaf: "🍃 Leaf",
                part_fruit: "🥭 Fruit",
                part_other: "❓ Other",
                obs_label: "Worker Symptoms & Observations",
                obs_placeholder: "Describe symptoms, onset timing, or nearby trees...",
                submit_btn: "ANALYZE INSPECTION WITH VISION AI",
                brief_title: "AI Agronomic Inspection Brief",
                brief_sub: "Structured multimodal vision triage & evidence summary.",
                empty_title: "Inspection Brief Ready for Evidence",
                empty_desc: "Upload a photo, enter orchard notes or select a demo preset scenario on the left, then click Analyze Inspection.",
                guardrail: "Agronomic Guardrail: AI analysis supports triage. Certified agronomist/manager must verify before treatment.",
                summary_hdr: "Executive Triage Summary:",
                evidence_hdr: "Physical Evidence",
                hypo_hdr: "Diagnostic Hypotheses",
                questions_hdr: "Field Worker Questions",
                checks_hdr: "Next Evidence Checks",
                unconfirmed: "Unconfirmed",
                quality: "📷 Quality:",
                worker_note: "Worker Note:",
                case_ref: "CASE REF:",
                refresh_btn: "Refresh Database",
                cases_title: "Orchard Case Database",
                cases_sub: "Central audit log of submitted field inspection reports.",
                mark_reviewed: "Mark as Reviewed",
                logout: "Logout"
            },
            mr: {
                app_sub: "हापूस आंबा बाग बहुभाषिक एआय रोग शोध प्रणाली (कोकण)",
                nav_new: "नवीन बाग तपासणी",
                nav_cases: "बाग केस ग्रंथालय",
                nav_arch: "प्रणाली रचना व सुरक्षा",
                preset_label: "त्वरित नमुना नमुने:",
                preset_1: "🍃 नमुना १: करपा (अँथ्रॅक्नोस) डाग",
                preset_2: "🥭 नमुना २: फळमाशीचे मऊ छिद्र",
                preset_3: "🌫️ नमुना ३: कमी प्रकाशातील पाने",
                field_title: "शेतकऱ्यांची लक्षण नोंदणी",
                field_sub: "झाडाचा व फळाचा सुस्पष्ट फोटो अपलोड करा.",
                photo_label: "पाने / फळांचे फोटो पुरावे",
                upload_title: "इथे फोटो अपलोड करण्यासाठी क्लिक करा",
                upload_sub: "JPG, PNG, WEBP फोटो १० MB पर्यंत",
                location_label: "झाड क्र. / बाग विभाग (ब्लॉक)",
                location_placeholder: "उदा. ब्लॉक अ / रांग ४ / झाड १८",
                subject_label: "तपासणीचा मुख्य भाग",
                part_leaf: "🍃 पान",
                part_fruit: "🥭 फळ",
                part_other: "❓ इतर",
                obs_label: "कामगार / शेतकऱ्यांचे निरीक्षण व लक्षणे",
                obs_placeholder: "पानांवरील किंवा फळांवरील लक्षणे, डाग, पाऊस किंवा हवामानाची माहिती लिहा...",
                submit_btn: "व्हिजन AI द्वारे रोगाची तपासणी करा",
                brief_title: "एआय कृषी रोग तपासणी अहवाल",
                brief_sub: "संरचित बहुभाषिक एआय वर्गीकरण आणि पुरावा सारांश.",
                empty_title: "तपासणी अहवाल तयार आहे",
                empty_desc: "डावीकडे फोटो अपलोड करा किंवा नमुना निवडा, नंतर तपासणी करा बटणावर क्लिक करा.",
                guardrail: "कृषी सुरक्षा नियम: हे AI विश्लेषण केवळ निदानास मदत करते. उपचारापूर्वी अधिकृत कृषी तज्ञांचा सल्ला आवश्यक आहे.",
                summary_hdr: "कार्यकारी रोग सारांश:",
                evidence_hdr: "भौतिक लक्षणे व पुरावे",
                hypo_hdr: "संभाव्य रोग / निदान अंदाज",
                questions_hdr: "शेतकऱ्यांसाठी विचारण्याचे प्रश्न",
                checks_hdr: "पुढील तपासणीची पावले",
                unconfirmed: "अपुष्टीकृत",
                quality: "📷 फोटो गुणवत्ता:",
                worker_note: "कामगाराची नोंद:",
                case_ref: "केस संदर्भ:",
                refresh_btn: "डेटाबेस अपडेट करा",
                cases_title: "बाग केस डेटाबेस",
                cases_sub: "सबमिट केलेल्या सर्व शेत तपासणी अहवालांची मध्यवर्ती नोंद.",
                mark_reviewed: "तपासले म्हणून चिन्हांकित करा",
                logout: "बाहेर पडा"
            },
            hi: {
                app_sub: "हापुस आम बाग बहुभाषी एआई रोग निदान प्लेटफॉर्म",
                nav_new: "नया बाग निरीक्षण",
                nav_cases: "बाग केस पुस्तकालय",
                nav_arch: "प्रणाली वास्तुकला और सुरक्षा",
                preset_label: "त्वरित डेमो नमूने:",
                preset_1: "🍃 नमूना १: एंथ्रेक्नोज (करपा) धब्बे",
                preset_2: "🥭 नमूना २: फल मक्खी का डंक",
                preset_3: "🌫️ नमूना ३: कम रोशनी वाले पत्ते",
                field_title: "खेत लक्षण कैप्चर",
                field_sub: "पेड़ और फल के संदर्भ के साथ फोटो अपलोड करें।",
                photo_label: "पत्ती / फल फोटो प्रमाण",
                upload_title: "यहाँ क्लिक करके फोटो अपलोड करें",
                upload_sub: "JPG, PNG, WEBP फोटो 10MB तक",
                location_label: "पेड़ संख्या / बाग ब्लॉक",
                location_placeholder: "जैसे: ब्लॉक ए / पंक्ति ४ / पेड़ १८",
                subject_label: "निरीक्षण का विषय",
                part_leaf: "🍃 पत्ती",
                part_fruit: "🥭 फल",
                part_other: "❓ अन्य",
                obs_label: "किसान / कार्यकर्ता के लक्षण और अवलोकन",
                obs_placeholder: "पत्तियों या फलों पर धब्बे, मौसम और लक्षणों का विवरण लिखें...",
                submit_btn: "विज़न AI से निरीक्षण की जाँच करें",
                brief_title: "एआई कृषि रोग निरीक्षण रिपोर्ट",
                brief_sub: "संरचित बहुभाषी एआई वर्गीकरण और साक्ष्य सारांश।",
                empty_title: "निरीक्षण रिपोर्ट तैयार है",
                empty_desc: "बाईं ओर फोटो अपलोड करें या नमूना चुनें, फिर निरीक्षण जाँच पर क्लिक करें।",
                guardrail: "कृषि सुरक्षा निर्देश: यह AI विश्लेषण केवल प्राथमिक सहायता है। उपचार से पहले प्रमाणित कृषि विशेषज्ञ से पुष्टि करें।",
                summary_hdr: "काल्पनिक विश्लेषण सारांश:",
                evidence_hdr: "भौतिक लक्षण और साक्ष्य",
                hypo_hdr: "संभावित रोग और निदान",
                questions_hdr: "किसानों के लिए फॉलो-अप प्रश्न",
                checks_hdr: "अगले निरीक्षण कदम",
                unconfirmed: "अपुष्ट",
                quality: "📷 फोटो गुणवत्ता:",
                worker_note: "कार्यकर्ता टिप्पणी:",
                case_ref: "केस संदर्भ:",
                refresh_btn: "डेटाबेस रीफ्रेश करें",
                cases_title: "बाग केस डेटाबेस",
                cases_sub: "दर्ज की गई सभी कृषि निरीक्षण रिपोर्टों का केंद्रीय लॉग।",
                mark_reviewed: "समीक्षित के रूप में चिह्नित करें",
                logout: "लॉग आउट"
            }
        };

        function changeLanguage(lang) {
            currentLang = lang;
            const dict = I18N_DICT[lang] || I18N_DICT['en'];
            
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (dict[key]) el.innerHTML = dict[key];
            });

            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (dict[key]) el.placeholder = dict[key];
            });
            
            if (window.lastCaseData) {
                renderBrief(window.lastCaseData);
            }
        }

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
            canvas.width = 600; canvas.height = 600;
            const ctx = canvas.getContext('2d');

            if (num === 1) {
                // REALISTIC ALPHONSO MANGO LEAF WITH ANTHRACNOSE LESIONS
                const bgGrad = ctx.createRadialGradient(300, 300, 50, 300, 300, 350);
                bgGrad.addColorStop(0, '#1e293b');
                bgGrad.addColorStop(1, '#0f172a');
                ctx.fillStyle = bgGrad;
                ctx.fillRect(0, 0, 600, 600);

                // Leaf Shadow
                ctx.save();
                ctx.shadowColor = 'rgba(0,0,0,0.6)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 10;
                ctx.shadowOffsetY = 15;

                // Leaf outline
                ctx.beginPath();
                ctx.moveTo(300, 60);
                ctx.bezierCurveTo(460, 180, 480, 420, 300, 540);
                ctx.bezierCurveTo(120, 420, 140, 180, 300, 60);
                ctx.closePath();

                const leafGrad = ctx.createLinearGradient(150, 150, 450, 450);
                leafGrad.addColorStop(0, '#16a34a');
                leafGrad.addColorStop(0.5, '#15803d');
                leafGrad.addColorStop(1, '#166534');
                ctx.fillStyle = leafGrad;
                ctx.fill();
                ctx.restore();

                // Central Vein
                ctx.beginPath();
                ctx.moveTo(300, 60);
                ctx.quadraticCurveTo(302, 300, 300, 540);
                ctx.strokeStyle = '#a3e635';
                ctx.lineWidth = 5;
                ctx.stroke();

                // Secondary Veins
                const veins = [140, 220, 300, 380, 440];
                veins.forEach(y => {
                    ctx.beginPath();
                    ctx.moveTo(300, y);
                    ctx.quadraticCurveTo(370, y - 30, 430, y - 50);
                    ctx.moveTo(300, y);
                    ctx.quadraticCurveTo(230, y - 30, 170, y - 50);
                    ctx.strokeStyle = 'rgba(163, 230, 53, 0.4)';
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                });

                // Anthracnose Lesions (Dark spots with yellow halos)
                const spots = [
                    { x: 340, y: 220, r: 28 },
                    { x: 240, y: 310, r: 22 },
                    { x: 370, y: 380, r: 35 },
                    { x: 210, y: 190, r: 18 },
                    { x: 280, y: 440, r: 25 }
                ];

                spots.forEach(s => {
                    // Yellow halo
                    ctx.beginPath();
                    ctx.arc(s.x, s.y, s.r + 8, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(250, 204, 21, 0.7)';
                    ctx.fill();

                    // Dark necrotic center
                    ctx.beginPath();
                    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                    const spotGrad = ctx.createRadialGradient(s.x, s.y, 2, s.x, s.y, s.r);
                    spotGrad.addColorStop(0, '#1c1917');
                    spotGrad.addColorStop(0.7, '#451a03');
                    spotGrad.addColorStop(1, '#78350f');
                    ctx.fillStyle = spotGrad;
                    ctx.fill();
                });

                // Cyber Reticle Overlay
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 2;
                ctx.setLineDash([6, 6]);
                ctx.strokeRect(290, 170, 130, 260);
                ctx.setLineDash([]);
                ctx.fillStyle = '#38bdf8';
                ctx.font = 'bold 14px monospace';
                ctx.fillText('[SCAN TARGET: ANTHRACNOSE_01]', 290, 160);

            } else if (num === 2) {
                // REALISTIC RIPE ALPHONSO MANGO WITH FRUIT FLY PUNCTURE
                const bgGrad = ctx.createRadialGradient(300, 300, 50, 300, 300, 350);
                bgGrad.addColorStop(0, '#1e1b4b');
                bgGrad.addColorStop(1, '#090d16');
                ctx.fillStyle = bgGrad;
                ctx.fillRect(0, 0, 600, 600);

                // Alphonso Mango Shape
                ctx.save();
                ctx.shadowColor = 'rgba(0,0,0,0.7)';
                ctx.shadowBlur = 25;
                ctx.shadowOffsetY = 15;

                ctx.beginPath();
                ctx.moveTo(300, 100);
                ctx.bezierCurveTo(480, 150, 510, 420, 330, 520);
                ctx.bezierCurveTo(240, 560, 120, 440, 160, 280);
                ctx.bezierCurveTo(180, 160, 240, 90, 300, 100);
                ctx.closePath();

                const mangoGrad = ctx.createRadialGradient(280, 220, 40, 320, 340, 260);
                mangoGrad.addColorStop(0, '#fef08a');
                mangoGrad.addColorStop(0.4, '#eab308');
                mangoGrad.addColorStop(0.75, '#f97316');
                mangoGrad.addColorStop(1, '#dc2626');
                ctx.fillStyle = mangoGrad;
                ctx.fill();
                ctx.restore();

                // Stem
                ctx.beginPath();
                ctx.arc(300, 110, 14, 0, Math.PI * 2);
                ctx.fillStyle = '#713f12';
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(300, 110);
                ctx.lineTo(290, 60);
                ctx.strokeStyle = '#451a03';
                ctx.lineWidth = 8;
                ctx.lineCap = 'round';
                ctx.stroke();

                // Fruit Fly Puncture Lesion
                ctx.beginPath();
                ctx.arc(340, 220, 32, 0, Math.PI * 2);
                const puncGrad = ctx.createRadialGradient(340, 220, 4, 340, 220, 32);
                puncGrad.addColorStop(0, '#1c1917');
                puncGrad.addColorStop(0.5, '#78350f');
                puncGrad.addColorStop(0.8, 'rgba(217, 119, 6, 0.8)');
                puncGrad.addColorStop(1, 'transparent');
                ctx.fillStyle = puncGrad;
                ctx.fill();

                ctx.beginPath();
                ctx.arc(340, 220, 5, 0, Math.PI * 2);
                ctx.fillStyle = '#0f172a';
                ctx.fill();

                // Reticle Target
                ctx.strokeStyle = '#f43f5e';
                ctx.lineWidth = 2;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.arc(340, 220, 45, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
                ctx.fillStyle = '#f43f5e';
                ctx.font = 'bold 14px monospace';
                ctx.fillText('[TARGET: FRUIT_FLY_PUNCTURE]', 250, 160);

            } else {
                // BLURRY CANOPY FOLIAGE
                ctx.fillStyle = '#020617';
                ctx.fillRect(0, 0, 600, 600);

                const colors = ['rgba(22,101,52,0.4)', 'rgba(21,128,61,0.5)', 'rgba(30,58,138,0.3)', 'rgba(51,65,85,0.6)'];
                for (let i = 0; i < 40; i++) {
                    const x = (Math.sin(i * 13) * 0.5 + 0.5) * 600;
                    const y = (Math.cos(i * 17) * 0.5 + 0.5) * 600;
                    const r = 40 + (i % 5) * 25;
                    ctx.beginPath();
                    ctx.arc(x, y, r, 0, Math.PI * 2);
                    ctx.fillStyle = colors[i % colors.length];
                    ctx.fill();
                }

                ctx.fillStyle = 'rgba(2, 6, 23, 0.4)';
                ctx.fillRect(0, 0, 600, 600);

                ctx.strokeStyle = '#fbbf24';
                ctx.lineWidth = 2;
                ctx.strokeRect(50, 50, 500, 500);
                ctx.fillStyle = '#fbbf24';
                ctx.font = 'bold 16px monospace';
                ctx.fillText('[AMBIGUOUS CANOPY LIGHTING DETECTED]', 120, 90);
            }

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

        let loaderInterval = null;
        let loaderStartTime = 0;

        function startAgriLoader() {
            loaderStartTime = Date.now();
            
            // Populate cyber scanner frame image
            const scanImg = document.getElementById('loader-scan-img');
            const preview = document.getElementById('image-preview');
            if (scanImg && preview && preview.src) {
                scanImg.src = preview.src;
            }

            updateAgriLoaderState(0);
            
            if (loaderInterval) clearInterval(loaderInterval);
            loaderInterval = setInterval(() => {
                const elapsed = (Date.now() - loaderStartTime) / 1000;
                const timerEl = document.getElementById('loader-timer');
                if (timerEl) timerEl.innerText = elapsed.toFixed(1) + 's';
                updateAgriLoaderState(elapsed);
            }, 100);
        }

        function stopAgriLoader() {
            if (loaderInterval) {
                clearInterval(loaderInterval);
                loaderInterval = null;
            }
        }

        function updateAgriLoaderState(elapsed) {
            const titleEl = document.getElementById('loader-stage-title');
            const descEl = document.getElementById('loader-stage-desc');
            const logEl = document.getElementById('loader-log-feed');
            const latencyEl = document.getElementById('loader-tensor-latency');
            const boxEl = document.getElementById('loader-bounding-box');
            const s1 = document.getElementById('loader-step-1');
            const s2 = document.getElementById('loader-step-2');
            const s3 = document.getElementById('loader-step-3');
            const s4 = document.getElementById('loader-step-4');

            const setStep = (el, active) => {
                if (!el) return;
                if (active) {
                    el.className = 'py-2 px-1 rounded-lg bg-emerald-500/20 border border-emerald-500/60 text-emerald-300 text-[10px] font-bold text-center shadow-md shadow-emerald-500/30 transition-all duration-300';
                } else {
                    el.className = 'py-2 px-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-500 text-[10px] font-bold text-center transition-all duration-300';
                }
            };

            if (elapsed < 1.5) {
                if (titleEl) titleEl.innerHTML = '🌱 1. Visual Matrix Scanning';
                if (descEl) descEl.innerText = 'Preprocessing canopy photo & segmenting leaf/fruit boundaries...';
                if (logEl) logEl.innerHTML = '> Segmenting 512x512 RGB tensors... [Visual Patches: 1024]';
                if (latencyEl) latencyEl.innerText = '94ms/tok';
                if (boxEl) { boxEl.style.top = '15%'; boxEl.style.left = '20%'; boxEl.style.width = '40%'; boxEl.style.height = '45%'; }
                setStep(s1, true); setStep(s2, false); setStep(s3, false); setStep(s4, false);
            } else if (elapsed < 3.5) {
                if (titleEl) titleEl.innerHTML = '🧠 2. Qwen3-VL Tensor Alignment';
                if (descEl) descEl.innerText = 'Cross-examining visual lesions through 4-bit transformer weights...';
                if (logEl) logEl.innerHTML = '> Qwen3-VL 4-bit NF4 weights processing patch tokens...';
                if (latencyEl) latencyEl.innerText = '142ms/tok';
                if (boxEl) { boxEl.style.top = '25%'; boxEl.style.left = '30%'; boxEl.style.width = '50%'; boxEl.style.height = '50%'; }
                setStep(s1, true); setStep(s2, true); setStep(s3, false); setStep(s4, false);
            } else if (elapsed < 5.5) {
                if (titleEl) titleEl.innerHTML = '🔬 3. ICAR Diagnostic Rules Engine';
                if (descEl) descEl.innerText = 'Matching observed lesions with ICAR-CISH mango disease guidelines...';
                if (logEl) logEl.innerHTML = '> Evaluating rules: Anthracnose vs. Fruit Fly vs. Powdery Mildew...';
                if (latencyEl) latencyEl.innerText = '118ms/tok';
                if (boxEl) { boxEl.style.top = '20%'; boxEl.style.left = '25%'; boxEl.style.width = '55%'; boxEl.style.height = '55%'; }
                setStep(s1, true); setStep(s2, true); setStep(s3, true); setStep(s4, false);
            } else {
                if (titleEl) titleEl.innerHTML = '📋 4. Synthesizing Orchard Brief';
                if (descEl) descEl.innerText = 'Formulating physical evidence, hypotheses & manager action items...';
                if (logEl) logEl.innerHTML = '> Finalizing executive brief & agronomic guardrails...';
                if (latencyEl) latencyEl.innerText = '82ms/tok';
                if (boxEl) { boxEl.style.top = '18%'; boxEl.style.left = '22%'; boxEl.style.width = '60%'; boxEl.style.height = '60%'; }
                setStep(s1, true); setStep(s2, true); setStep(s3, true); setStep(s4, true);
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
            startAgriLoader();

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
                stopAgriLoader();
                alert('Error submitting inspection: ' + err.message);
                document.getElementById('brief-loading').classList.add('hidden');
                document.getElementById('brief-empty').classList.remove('hidden');
            }
        }

        function renderBrief(c) {
            window.lastCaseData = c;
            stopAgriLoader();
            document.getElementById('brief-loading').classList.add('hidden');
            document.getElementById('brief-content').classList.remove('hidden');
            
            const dict = I18N_DICT[currentLang] || I18N_DICT['en'];
            const rev = c.revisions && c.revisions.length > 0 ? c.revisions[c.revisions.length - 1] : null;
            const res = rev ? rev.analysis : null;

            let html = `
                <div class="glass-card p-5 rounded-2xl border border-emerald-500/20 space-y-4">
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-mono font-bold tracking-widest text-slate-400 bg-slate-900 px-2.5 py-1 rounded-md">${dict.case_ref} ${c.id.substring(0,8)}</span>
                        <span class="text-xs font-bold ${c.status === 'reviewed' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' : 'text-amber-400 bg-amber-500/10 border-amber-500/30'} border px-3 py-1 rounded-full">● ${c.status.toUpperCase()}</span>
                    </div>
                    <div>
                        <h4 class="text-xl font-extrabold text-white">📍 ${c.report.location} <span class="text-xs text-slate-400 font-normal">(${c.report.part})</span></h4>
                        <div class="mt-2 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border-l-4 border-emerald-500">
                            <strong>${dict.worker_note}</strong> "${c.report.observation}"
                        </div>
                    </div>
            `;

            if (res) {
                html += `
                    <div class="flex items-center justify-between text-xs border-t border-slate-800 pt-3">
                        <span class="px-2.5 py-1 rounded-md text-[11px] font-bold ${res.image_quality === 'usable' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'}">${dict.quality} ${res.image_quality.toUpperCase()}</span>
                        <span class="text-[11px] text-slate-400">${rev.model} · ${rev.seconds}s latency</span>
                    </div>

                    <div class="bg-gradient-to-r from-emerald-950/40 to-green-900/20 border border-emerald-500/30 p-4 rounded-xl text-xs text-emerald-200">
                        <strong>${dict.summary_hdr}</strong><br>${res.summary}
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div class="glass-card p-4 rounded-xl border-l-4 border-emerald-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-magnifying-glass text-emerald-400"></i> ${dict.evidence_hdr}</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.observations.map(o => `<li>${o}</li>`).join('') || '<li>None isolated</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-amber-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-lightbulb text-amber-400"></i> ${dict.hypo_hdr} <span class="text-[9px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded">${dict.unconfirmed}</span></div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.possible_explanations.map(e => `<li>${e}</li>`).join('') || '<li>Insufficient evidence</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-blue-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-circle-question text-blue-400"></i> ${dict.questions_hdr}</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.questions.map(q => `<li>${q}</li>`).join('') || '<li>None required</li>'}</ul>
                        </div>
                        <div class="glass-card p-4 rounded-xl border-l-4 border-teal-500 space-y-1">
                            <div class="font-bold text-white flex items-center gap-1.5"><i class="fa-solid fa-clipboard-check text-teal-400"></i> ${dict.checks_hdr}</div>
                            <ul class="list-disc pl-4 text-slate-300 space-y-1">${res.next_checks.map(n => `<li>${n}</li>`).join('') || '<li>Standard monitoring</li>'}</ul>
                        </div>
                    </div>
                `;
            }

            html += `
                <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-[11px] text-amber-300 flex items-start gap-2">
                    <i class="fa-solid fa-triangle-exclamation text-amber-400 mt-0.5"></i>
                    <div>${dict.guardrail}</div>
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
    
def create_public_tunnel(port):
    """Generates a direct public URL with seamless fallback across Gradio, Cloudflare, and Localtunnel."""
    # 1. Gradio FRPC Tunnel (gradio.live)
    try:
        token = secrets.token_urlsafe(16)
        tunnel = Tunnel("gradio.live", 7000, "127.0.0.1", port, token, None)
        url = tunnel.start_tunnel()
        if url:
            return url, "Gradio Live"
    except Exception as exc:
        print(f"Gradio tunnel unavailable: {exc}. Trying Cloudflare Tunnel...", flush=True)

    # 2. Cloudflare Tunnel (trycloudflare.com) - Direct browser access with zero IP verification prompts
    try:
        import subprocess, time, re
        cmd = ["npx", "-y", "@cloudflare/cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(30):
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.3)
                continue
            match = re.search(r"https://[-a-zA-Z0-9.]+\.trycloudflare\.com", line)
            if match:
                return match.group(0), "Cloudflare"
    except Exception as cf_exc:
        print(f"Cloudflare tunnel error: {cf_exc}. Trying Localtunnel fallback...", flush=True)

    # 3. Localtunnel fallback (loca.lt)
    try:
        import subprocess, time, urllib.request
        host_ip = "Unknown"
        try:
            with urllib.request.urlopen("https://api.ipify.org") as resp:
                host_ip = resp.read().decode('utf-8').strip()
        except Exception:
            pass

        proc = subprocess.Popen(["npx", "-y", "localtunnel", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(20):
            line = proc.stdout.readline()
            if "url is:" in line.lower():
                url = line.split("is:")[-1].strip()
                return url, f"Localtunnel (IP Passcode: {host_ip})"
    except Exception as lt_exc:
        print(f"Localtunnel warning: {lt_exc}", flush=True)

    return None, "Local Server"


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
    
    port = 7860
    if args.share:
        public_url, provider = create_public_tunnel(port)

        print(f"\n=======================================================", flush=True)
        print(f"🚀 Hapus Scout Enterprise Live App: {public_url or f'http://127.0.0.1:{port}'}", flush=True)
        print(f"📡 Tunnel Provider: {provider}", flush=True)
        print(f"🔑 App Passcode: scout / scout123", flush=True)
        print(f"=======================================================\n", flush=True)
        uvicorn.run(fastapi_app, host="127.0.0.1", port=port)
    else:
        print(f"Launching Hapus Scout Enterprise on http://127.0.0.1:{port}...", flush=True)
        uvicorn.run(fastapi_app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
