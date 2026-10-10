// Leaderboard live syncing & projector controller

let lastLeaderboardData = null;
let pollInterval = null;
let isProjector = false;

function initLeaderboard() {
    pollLeaderboard();
    pollInterval = setInterval(pollLeaderboard, 4000);

    // ESC to exit projector mode
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isProjector) {
            toggleProjectorMode();
        }
    });
}

function pollLeaderboard() {
    fetch('/api/leaderboard')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                handleLeaderboardUpdate(data);
            }
        })
        .catch(err => console.error('Error polling leaderboard:', err));
}

function handleLeaderboardUpdate(data) {
    const squads = data.leaderboard;
    const totalFlowers = data.total_flowers || 20;

    // Detect if rank 1 changed or points increased
    if (lastLeaderboardData) {
        const prevFirst = lastLeaderboardData[0];
        const newFirst = squads[0];

        if (newFirst && prevFirst && (newFirst.id !== prevFirst.id || newFirst.flowers_count > prevFirst.flowers_count)) {
            triggerConfetti();
            playSuccessSound();
        }
    }
    lastLeaderboardData = squads;

    renderLeaderboardTable(squads, totalFlowers);
}

function renderLeaderboardTable(squads, totalFlowers) {
    const tbody = document.getElementById('leaderboard-tbody');
    if (!tbody) return;

    if (!squads || squads.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="py-8 text-center text-slate-500 italic">No teams registered yet.</td></tr>';
        return;
    }

    let html = '';
    squads.forEach((sq, idx) => {
        const rank = idx + 1;
        const rankBadgeClass = rank === 1 ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/30' :
                               (rank === 2 ? 'bg-slate-300 text-slate-950' :
                               (rank === 3 ? 'bg-amber-700 text-white' : 'bg-slate-800 text-slate-300'));
        
        const pct = Math.round((sq.flowers_count / totalFlowers) * 100);

        html += `
        <tr class="rank-row hover:bg-slate-800/40 transition ${rank === 1 ? 'bg-amber-950/10' : ''}">
            <td class="py-4 px-4 text-center">
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full font-mono font-bold text-xs ${rankBadgeClass}">
                    ${rank}
                </span>
            </td>

            <td class="py-4 px-4">
                <div class="font-bold text-white flex items-center gap-2">
                    <span>${escapeHtml(sq.name)}</span>
                    ${rank === 1 ? '<span class="text-xs text-amber-400">👑</span>' : ''}
                </div>
            </td>

            <td class="py-4 px-4 text-slate-300 text-xs font-medium">
                ${escapeHtml(sq.captain)}
            </td>

            <td class="py-4 px-4">
                <div class="flex items-center justify-center gap-2">
                    <span class="font-mono font-bold text-white text-sm">${sq.flowers_count}</span>
                    <span class="text-xs text-slate-500">/ ${totalFlowers}</span>
                </div>
                <div class="w-24 mx-auto bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
                    <div class="bg-gradient-to-r from-google-blue to-google-green h-full rounded-full transition-all duration-500"
                         style="width: ${pct}%"></div>
                </div>
            </td>

            <td class="py-4 px-4 text-right">
                <span class="font-mono font-extrabold text-amber-400 text-base">
                    ${sq.total_points}
                </span>
                <span class="text-xs text-slate-500 font-mono">points</span>
            </td>

            <td class="py-4 px-4 text-right">
                <a href="/squad/${sq.id}" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold transition">
                    <span>👥</span>
                    <span>Team Details</span>
                </a>
            </td>
        </tr>
        `;
    });

    tbody.innerHTML = html;
}

function toggleProjectorMode() {
    isProjector = !isProjector;
    document.body.classList.toggle('projector-mode', isProjector);
    
    const exitBar = document.getElementById('exit-projector-bar');
    if (exitBar) {
        exitBar.classList.toggle('hidden', !isProjector);
    }

    if (isProjector && document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
    } else if (!isProjector && document.fullscreenElement) {
        document.exitFullscreen().catch(() => {});
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

window.addEventListener('DOMContentLoaded', initLeaderboard);
