// GDG x Black Clover - Client Controller & Synthesizer

let soundEnabled = true;
let audioCtx = null;

function getAudioContext() {
    if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function toggleAudio() {
    soundEnabled = !soundEnabled;
    const icon = document.getElementById('sfx-icon');
    if (icon) {
        icon.innerText = soundEnabled ? '🔊' : '🔇';
    }
    localStorage.setItem('gdg_sfx_enabled', soundEnabled);
}

// Synthesize Magical Anime Chime (Flower Discovered)
function playSuccessSound() {
    if (!soundEnabled) return;
    try {
        const ctx = getAudioContext();
        const now = ctx.currentTime;
        
        // C-E-G-B-C arpeggio with crystalline sine waves
        const notes = [523.25, 659.25, 783.99, 987.77, 1046.50];
        notes.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + i * 0.08);
            
            gain.gain.setValueAtTime(0, now + i * 0.08);
            gain.gain.linearRampToValueAtTime(0.2, now + i * 0.08 + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.4);
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            osc.start(now + i * 0.08);
            osc.stop(now + i * 0.08 + 0.45);
        });
    } catch (e) {
        console.warn('Audio not allowed yet:', e);
    }
}

// Synthesize Error Buzzer
function playErrorSound() {
    if (!soundEnabled) return;
    try {
        const ctx = getAudioContext();
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.linearRampToValueAtTime(90, now + 0.25);
        
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.start(now);
        osc.stop(now + 0.25);
    } catch (e) {}
}

// Google 4-Color Confetti Burst
function triggerConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 80,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#FFFFFF']
        });
    }
}

// Global Claim Modal Handlers
function openClaimModal() {
    const modal = document.getElementById('claim-modal');
    if (!modal) return;
    
    populateSquadDropdown();
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Focus passcode input
    setTimeout(() => {
        const input = document.getElementById('claim-passcode');
        if (input) input.focus();
    }, 100);
}

function openClaimModalWithFlower(flowerId, preselectedSquadId) {
    openClaimModal();
    if (preselectedSquadId) {
        const squadSelect = document.getElementById('claim-squad-select');
        if (squadSelect) squadSelect.value = preselectedSquadId;
    }
}

function closeClaimModal() {
    const modal = document.getElementById('claim-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    const msg = document.getElementById('claim-status-msg');
    if (msg) msg.className = 'hidden';
}

function populateSquadDropdown() {
    const select = document.getElementById('claim-squad-select');
    if (!select || select.children.length > 1) return;

    fetch('/api/leaderboard')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success' && data.leaderboard) {
                select.innerHTML = '<option value="">-- Choose a team --</option>';
                data.leaderboard.forEach(sq => {
                    const opt = document.createElement('option');
                    opt.value = sq.id;
                    opt.textContent = `${sq.name} (${sq.flowers_count}/20 flowers)`;
                    select.appendChild(opt);
                });
            }
        })
        .catch(err => console.error('Error fetching squads:', err));
}

function submitFlowerClaim(event) {
    event.preventDefault();
    const squadId = document.getElementById('claim-squad-select').value;
    const passcode = document.getElementById('claim-passcode').value.trim();
    const memberName = document.getElementById('claim-member-name').value.trim();
    const statusMsg = document.getElementById('claim-status-msg');
    const submitBtn = document.getElementById('claim-submit-btn');

    if (!squadId || !passcode) {
        showStatus('Please select a team and enter the flower code.', 'error');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = 'Submitting...';

    fetch('/api/claim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            squad_id: squadId,
            passcode: passcode,
            claimed_by: memberName || 'Team member'
        })
    })
    .then(r => r.json())
    .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>⚡</span><span>Submit Claim</span>';

        if (data.status === 'success') {
            playSuccessSound();
            triggerConfetti();
            showStatus(`✨ ${data.message} (+${data.flower.points} points)`, 'success');
            
            // Clear inputs
            document.getElementById('claim-passcode').value = '';

            setTimeout(() => {
                closeClaimModal();
                // If on leaderboard or squad page, reload or refresh
                if (window.location.pathname === '/leaderboard' || window.location.pathname.startsWith('/squad/')) {
                    window.location.reload();
                }
            }, 1800);
        } else {
            playErrorSound();
            showStatus(`⚠️ ${data.message}`, 'error');
        }
    })
    .catch(err => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>⚡</span><span>Submit Claim</span>';
        playErrorSound();
        showStatus('Network connection error.', 'error');
    });
}

function showStatus(text, type) {
    const el = document.getElementById('claim-status-msg');
    if (!el) return;
    el.innerText = text;
    el.classList.remove('hidden', 'bg-emerald-950/80', 'text-emerald-300', 'bg-rose-950/80', 'text-rose-300', 'border-emerald-600', 'border-rose-600');
    el.classList.add('border');

    if (type === 'success') {
        el.classList.add('bg-emerald-950/80', 'text-emerald-300', 'border-emerald-600');
    } else {
        el.classList.add('bg-rose-950/80', 'text-rose-300', 'border-rose-600');
    }
}

// Auto-fill from URL params (e.g. from QR code scan: /?passcode=BRIAR-01)
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const paramPasscode = urlParams.get('passcode');
    if (paramPasscode) {
        openClaimModal();
        const input = document.getElementById('claim-passcode');
        if (input) input.value = paramPasscode;
    }
});
