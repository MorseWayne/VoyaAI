// ========== Theme Management ==========
function initTheme() {
    const saved = localStorage.getItem('voyaai-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    applyTheme(theme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('voyaai-theme', theme);
    updateThemeIcons(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
}

function updateThemeIcons(theme) {
    // Desktop icons
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    if (sunIcon && moonIcon) {
        sunIcon.classList.toggle('hidden', theme !== 'dark');  // Show sun in dark (click to go light)
        moonIcon.classList.toggle('hidden', theme !== 'light'); // Show moon in light (click to go dark)
    }
    // Mobile icons
    document.querySelectorAll('.theme-icon-sun-m').forEach(el => el.classList.toggle('hidden', theme !== 'dark'));
    document.querySelectorAll('.theme-icon-moon-m').forEach(el => el.classList.toggle('hidden', theme !== 'light'));
}

function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
}

// Initialize theme immediately (before DOMContentLoaded to prevent flash)
initTheme();

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('voyaai-theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
    }
});

// Navigation and View Management
function showView(viewId) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => {
        el.classList.add('hidden');
    });
    
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
    });

    // Show selected view
    const viewEl = document.getElementById(`view-${viewId}`);
    if (viewEl) {
        viewEl.classList.remove('hidden');
    }
    
    // Add active class to selected nav item
    const navItem = document.getElementById(`nav-${viewId}`);
    if (navItem) {
        navItem.classList.add('active');
    }

    // Toggle navbar menu visibility: hide on home, show on other views
    const navMenu = document.getElementById('nav-menu');
    const navMobileBtn = document.getElementById('nav-mobile-btn');
    const isHome = viewId === 'home';

    if (navMenu) {
        if (isHome) {
            navMenu.classList.add('!hidden');
        } else {
            navMenu.classList.remove('!hidden');
        }
    }
    if (navMobileBtn) {
        if (isHome) {
            navMobileBtn.classList.add('!hidden');
        } else {
            navMobileBtn.classList.remove('!hidden');
        }
    }

    // Close mobile menu when switching views
    closeMobileMenu();

    // Load data if needed
    if (viewId === 'plans') {
        loadPlans();
    }
    if (viewId === 'home') {
        loadDashboardData();
    }

    // Scroll to top on view change
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function closeMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.add('hidden');
    }
}

// Dashboard Logic
async function loadDashboardData() {
    const listDiv = document.getElementById('dashboard-recent-plans');
    const countEl = document.getElementById('stats-plan-count');
    const cityEl = document.getElementById('stats-city-count');
    
    if (!listDiv) return;

    try {
        const response = await fetch('/travel/plans');
        const plans = await response.json();
        
        // Update Stats
        if (countEl) countEl.innerText = plans.length;
        if (cityEl) {
            const cities = new Set();
            plans.forEach(p => {
                if (p.start_location && p.start_location.city) cities.add(p.start_location.city);
                p.days?.forEach(d => {
                    if (d.city) cities.add(d.city);
                    d.segments?.forEach(s => {
                        if (s.origin?.city) cities.add(s.origin.city);
                        if (s.destination?.city) cities.add(s.destination.city);
                    });
                });
            });
            cityEl.innerText = cities.size;
        }

        // Render Recent Plans (Top 5)
        if (plans.length === 0) {
            listDiv.innerHTML = `
                <div class="text-center py-12 t-text-muted">
                    <i class="fas fa-wind text-3xl mb-3 opacity-50"></i>
                    <p>暂无行程，快去创建吧！</p>
                </div>
            `;
            return;
        }

        // Sort by created_at desc (assuming API returns them somewhat ordered or we sort here)
        // plans.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)); 

        listDiv.innerHTML = plans.slice(0, 10).map(plan => `
            <div onclick="viewPlan('${plan.id}')" class="rounded-xl p-4 cursor-pointer transition flex items-center justify-between group" style="background: var(--bg-card); border: 1px solid var(--border-color);">
                <div class="flex items-center gap-4 min-w-0">
                    <div class="w-10 h-10 rounded-lg flex items-center justify-center text-cyan-500 font-bold text-sm" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
                        ${(plan.days || []).length}天
                    </div>
                    <div class="min-w-0">
                        <h4 class="font-bold t-text truncate group-hover:text-cyan-500 transition">${plan.title || '未命名行程'}</h4>
                        <div class="text-xs t-text-muted flex items-center gap-2">
                            <span><i class="far fa-calendar-alt mr-1"></i> ${new Date(plan.created_at || Date.now()).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>${(plan.days || []).reduce((acc, d) => acc + (d.segments?.length||0), 0)} 个地点</span>
                        </div>
                    </div>
                </div>
                <div class="t-text-muted group-hover:text-cyan-500 transition">
                    <i class="fas fa-chevron-right"></i>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Dashboard load error:', error);
        listDiv.innerHTML = '<p class="text-center text-red-400 py-4">数据加载失败</p>';
    }
}

let currentPlanData = null;
let selectedStartLocation = null;
let startSearchResults = [];
let startSearchTimer = null;

// Route Planner Logic
async function optimizeRoute() {
    const city = document.getElementById('planner-city').value.trim();
    const locationsRaw = document.getElementById('planner-locations').value.trim();
    const strategy = document.getElementById('planner-strategy').value;
    const preference = document.getElementById('planner-preference').value;
    const resultsDiv = document.getElementById('planner-results');

    if (!locationsRaw) {
        alert('请输入至少两个地点');
        return;
    }

    const locations = locationsRaw.split('\n').map(l => l.trim()).filter(l => l);
    if (locations.length < 2) {
        alert('请至少输入两个地点');
        return;
    }

    // Show loading state
    resultsDiv.innerHTML = `
        <div class="text-center">
            <i class="fas fa-compass fa-spin text-5xl text-primary mb-4"></i>
            <p class="text-xl t-text-sub">正在为您规划最佳路线...</p>
            <p class="text-sm t-text-muted mt-2">正在计算距离和时间</p>
        </div>
    `;

    try {
        const response = await fetch('/travel/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                locations: locations,
                city: city,
                strategy: strategy,
                preference: preference
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '规划失败');
        }

        currentPlanData = data;
        renderRouteResults(data);

    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `
            <div class="text-center text-red-500">
                <i class="fas fa-exclamation-circle text-5xl mb-4"></i>
                <p class="text-xl">规划出错</p>
                <p class="mt-2">${error.message}</p>
            </div>
        `;
    }
}

function renderRouteResults(data) {
    const resultsDiv = document.getElementById('planner-results');
    
    if (!data.poi_details || data.poi_details.length === 0) {
        resultsDiv.innerHTML = '<p class="text-center t-text-muted">未找到合适的路线</p>';
        return;
    }

    const totalDuration = parseFloat(data.total_duration_hours) * 60; // hours to minutes
    const totalDist = data.total_distance_km;

    let html = `
        <div class="w-full p-6 rounded-xl shadow-sm" style="background: var(--bg-card); border: 1px solid var(--border-color);">
            <h3 class="text-xl font-bold t-heading mb-4 flex justify-between items-center">
                <span>规划结果</span>
                <div class="flex items-center gap-2">
                    <span class="text-sm font-normal t-text-sub px-3 py-1 rounded-full" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
                        总程: ${totalDist}km / 约 ${Math.round(totalDuration)}分钟
                    </span>
                    <button onclick="saveCurrentPlan()" class="text-sm bg-primary text-white px-3 py-2 rounded-lg hover:bg-cyan-600 transition flex items-center shadow-sm">
                        <i class="fas fa-plus mr-1"></i> 保存行程
                    </button>
                </div>
            </h3>
            <div class="relative ml-4 pl-8 space-y-8" style="border-left: 4px solid var(--border-color);">
    `;

    data.poi_details.forEach((loc, index) => {
        const isLast = index === data.poi_details.length - 1;
        const segment = !isLast ? data.segments[index] : null;

        html += `
            <div class="relative">
                <div class="absolute -left-[42px] text-cyan-500 w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-md" style="background: var(--bg-elevated); border: 2px solid var(--border-color);">
                    ${index + 1}
                </div>
                <div class="p-4 rounded-lg transition" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
                    <h4 class="font-bold text-lg t-text">${loc.name}</h4>
                    <p class="text-sm t-text-muted mt-1"><i class="fas fa-map-marker-alt mr-1"></i> ${loc.address || '地址未知'}</p>
                </div>
                ${!isLast && segment ? `
                    <div class="mt-4 mb-2 text-sm t-text-sub pl-2 flex items-center gap-2">
                        <i class="fas fa-arrow-down text-cyan-500"></i>
                        <span>约 ${segment.duration_m}分钟</span>
                        <span class="t-text-muted">|</span>
                        <span>${segment.distance_km}km</span>
                        <span class="t-text-muted">|</span>
                        <span class="text-xs t-text-sub px-2 py-0.5 rounded" style="background: var(--bg-inset); border: 1px solid var(--border-color);">${segment.mode}</span>
                    </div>
                ` : ''}
            </div>
        `;
    });

    html += `
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('items-center', 'justify-center'); // Align to top
}

async function saveCurrentPlan() {
    if (!currentPlanData) return;

    const city = document.getElementById('planner-city').value.trim() || '未知城市';
    
    // Construct Itinerary object
    const plan = {
        title: `${city}精彩游玩路线`,
        days: [{
             day_index: 1,
             city: city,
             segments: currentPlanData.segments.map((seg, idx) => {
                 const originPoi = currentPlanData.poi_details[idx];
                 const destPoi = currentPlanData.poi_details[idx+1];
                 const modeStr = (seg.mode || '').toString();

                 // Map mode strictly to enum
                 let mode = 'driving';
                 if (modeStr.includes('公交') || modeStr.includes('地铁') || modeStr.includes('Transit')) mode = 'transit';
                 if (modeStr.includes('步行')) mode = 'walking';
                 if (modeStr.includes('骑行')) mode = 'cycling';

                 // 城际/长途/跨城 与市内公交区分，用 details.display_label 存展示名
                 const details = {};
                 if (mode === 'transit' && (modeStr.includes('城际') || modeStr.includes('长途') || modeStr.includes('跨城'))) {
                     details.display_label = '城际交通';
                 }

                 return {
                     type: mode,
                     origin: {
                         name: originPoi.name,
                         lat: originPoi.lat,
                         lng: originPoi.lng,
                         address: originPoi.address,
                         city: city
                     },
                     destination: {
                         name: destPoi.name,
                         lat: destPoi.lat,
                         lng: destPoi.lng,
                         address: destPoi.address,
                         city: city
                     },
                     distance_km: parseFloat(seg.distance_km),
                     duration_minutes: parseFloat(seg.duration_m),
                     ...(Object.keys(details).length ? { details } : {})
                 };
             })
        }]
    };
    
    try {
        const response = await fetch('/travel/plans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(plan)
        });
        
        if (response.ok) {
            // Show toast or alert
            const btn = document.querySelector('button[onclick="saveCurrentPlan()"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> 已保存';
            btn.classList.replace('bg-primary', 'bg-green-500');
            
            setTimeout(() => {
                 showView('plans');
            }, 1000);
        } else {
            const err = await response.json();
            alert('保存失败: ' + (err.detail || '未知错误'));
        }
    } catch (e) {
        console.error(e);
        alert('保存出错，请检查网络');
    }
}

function formatDuration(seconds) {
    if (!seconds) return '0分钟';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
        return `${hours}小时${minutes}分钟`;
    }
    return `${minutes}分钟`;
}

/** 从 "YYYY-MM-DD HH:MM" 或 "HH:MM" 解析为时间戳（毫秒），用于计算时长 */
function parseTimeToMs(str) {
    if (!str || typeof str !== 'string') return NaN;
    const s = str.trim();
    if (/^\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}/.test(s)) {
        return new Date(s.replace(/-/g, '/')).getTime();
    }
    if (/^\d{1,2}:\d{2}/.test(s)) {
        const [h, m] = s.split(':').map(Number);
        return (h * 60 + m) * 60 * 1000;
    }
    return NaN;
}

/** 根据出发、到达时间字符串计算飞行/车程时长（秒），无效返回 0 */
function durationSecondsFromTimes(depStr, arrStr) {
    const depMs = parseTimeToMs(depStr);
    const arrMs = parseTimeToMs(arrStr);
    if (Number.isNaN(depMs) || Number.isNaN(arrMs) || arrMs <= depMs) return 0;
    return Math.round((arrMs - depMs) / 1000);
}

/** 午夜起分钟数 → "HH:MM" */
function minutesToHm(minutes) {
    if (minutes == null || minutes < 0) return '--';
    const h = Math.floor(minutes / 60) % 24;
    const m = Math.floor(minutes % 60);
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

/** "HH:MM" → 午夜起分钟数 */
function hmToMinutes(hm) {
    if (!hm || typeof hm !== 'string') return 0;
    const parts = hm.trim().match(/^(\d{1,2}):(\d{2})$/);
    if (!parts) return 0;
    return parseInt(parts[1], 10) * 60 + parseInt(parts[2], 10);
}

/** 时间字符串（"HH:MM" 或 "YYYY-MM-DD HH:MM"）→ 当日午夜起分钟数，无效返回 null */
function timeStringToMinutes(str) {
    if (!str || typeof str !== 'string') return null;
    const ms = parseTimeToMs(str.trim());
    if (Number.isNaN(ms)) return null;
    const d = new Date(ms);
    return d.getHours() * 60 + d.getMinutes();
}

/** 判断该段是否为明显导入的车票（航班/火车且同时有发车、到达时间） */
function segmentHasTicketTimes(seg) {
    if (!seg || (seg.type !== 'flight' && seg.type !== 'train')) return false;
    const dep = seg.details?.departure_time || seg.origin?.departure_time;
    const arr = seg.details?.arrival_time || seg.destination?.arrival_time;
    return !!(dep && arr && timeStringToMinutes(dep) != null && timeStringToMinutes(arr) != null);
}

/** 确保当天 location_stay_minutes 数组长度与地点数一致（segments.length + 1），缺省补 0 */
function ensureDayStayArray(day) {
    if (!day) return;
    const len = (day.segments && day.segments.length) ? day.segments.length + 1 : 1;
    if (!day.location_stay_minutes) day.location_stay_minutes = [];
    while (day.location_stay_minutes.length < len) {
        day.location_stay_minutes.push(0);
    }
    if (day.location_stay_minutes.length > len) {
        day.location_stay_minutes.length = len;
    }
}

/**
 * 根据「当日出发时间」「各点停留时间」「各段出行耗时」自动计算每个节点的到达与离开时间。
 * 若某段为明显导入的车票（航班/火车且有发车、到达时间），则该段的出发、到达时间以车票为准。
 */
function getDayArrivalTimes(day) {
    const segs = day.segments || [];
    const stay = day.location_stay_minutes || [];
    const startHm = day.start_time_hm || '08:00';
    let minutes = hmToMinutes(startHm);
    const result = [];
    for (let i = 0; i < segs.length; i++) {
        const seg = segs[i];
        const stayMin = Math.max(0, parseFloat(stay[i]) || 0);
        let departMin;
        let departHm;
        if (segmentHasTicketTimes(seg)) {
            const depStr = seg.details?.departure_time || seg.origin?.departure_time;
            const arrStr = seg.details?.arrival_time || seg.destination?.arrival_time;
            departMin = timeStringToMinutes(depStr);
            const arrMin = timeStringToMinutes(arrStr);
            result.push({
                arrivalMinutes: minutes,
                arrivalHm: minutesToHm(minutes),
                stayMinutes: stayMin,
                departureMinutes: departMin,
                departureHm: minutesToHm(departMin)
            });
            minutes = arrMin;
        } else {
            departMin = minutes + stayMin;
            departHm = minutesToHm(departMin);
            result.push({
                arrivalMinutes: minutes,
                arrivalHm: minutesToHm(minutes),
                stayMinutes: stayMin,
                departureMinutes: departMin,
                departureHm: departHm
            });
            const segDuration = Math.max(0, parseFloat(seg.duration_minutes) || 0);
            minutes = departMin + segDuration;
        }
    }
    const lastStay = Math.max(0, parseFloat(stay[segs.length]) || 0);
    result.push({
        arrivalMinutes: minutes,
        arrivalHm: minutesToHm(minutes),
        stayMinutes: lastStay,
        departureMinutes: minutes + lastStay,
        departureHm: minutesToHm(minutes + lastStay)
    });
    return result;
}

function formatDistance(meters) {
    if (!meters) return '0米';
    if (meters >= 1000) {
        return `${(meters / 1000).toFixed(1)}公里`;
    }
    return `${meters}米`;
}

// Plans Management
async function loadPlans() {
    const listDiv = document.getElementById('plans-list');
    listDiv.innerHTML = '<div class="col-span-full text-center py-12"><i class="fas fa-spinner fa-spin text-3xl text-primary"></i></div>';

    try {
        const response = await fetch('/travel/plans');
        const plans = await response.json();

        if (plans.length === 0) {
            listDiv.innerHTML = `
                <div class="col-span-full text-center py-12 rounded-xl border-dashed border-2" style="background: var(--bg-surface); border-color: var(--border-color);">
                    <i class="fas fa-inbox text-4xl t-text-muted mb-4"></i>
                    <p class="t-text-sub">暂无保存的行程</p>
                </div>
            `;
            return;
        }

        listDiv.innerHTML = plans.map(plan => `
            <div class="rounded-xl shadow-md hover:shadow-lg transition p-6 border-t-4 border-cyan-500 relative group" style="background: var(--bg-card); border-left: 1px solid var(--border-color); border-right: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color);">
                <button onclick="deletePlan('${plan.id}')" class="absolute top-4 right-4 t-text-muted hover:text-red-400 opacity-0 group-hover:opacity-100 transition">
                    <i class="fas fa-trash-alt"></i>
                </button>
                <h3 class="font-bold text-xl mb-2 t-heading truncate" title="${plan.title || '未命名行程'}">${plan.title || '未命名行程'}</h3>
                <div class="text-sm t-text-sub mb-4 space-y-1">
                    <p><i class="far fa-calendar-alt w-5 text-cyan-500"></i> ${new Date(plan.created_at || Date.now()).toLocaleDateString()}</p>
                    <p><i class="fas fa-map-marker-alt w-5 text-cyan-500"></i> ${plan.days ? plan.days.length : 0} 天行程</p>
                </div>
                <button onclick="viewPlan('${plan.id}')" class="w-full mt-2 t-text-sub hover:bg-cyan-600 hover:text-white font-medium py-2 rounded-lg transition" style="background: var(--bg-elevated); border: 1px solid var(--border-color);">
                    查看详情
                </button>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading plans:', error);
        listDiv.innerHTML = '<p class="text-center text-red-500 col-span-full">加载失败，请重试</p>';
    }
}

async function deletePlan(planId) {
    if (!confirm('确定要删除这个行程吗？')) return;
    try {
        await fetch(`/travel/plans/${planId}`, { method: 'DELETE' });
        loadPlans();
    } catch (error) {
        alert('删除失败');
    }
}

// --- Start Location Search (Create Plan) ---

function handleStartLocationSearch(keyword) {
    if (startSearchTimer) clearTimeout(startSearchTimer);
    const resultsDiv = document.getElementById('start-location-results');

    if (!keyword.trim()) {
        resultsDiv.classList.add('hidden');
        return;
    }

    startSearchTimer = setTimeout(async () => {
        resultsDiv.classList.remove('hidden');
        resultsDiv.innerHTML = '<div class="text-center py-3 t-text-muted text-sm"><i class="fas fa-spinner fa-spin"></i> 搜索中...</div>';

        try {
            const response = await fetch(`/travel/locations/tips?keywords=${encodeURIComponent(keyword)}&city=`);
            const data = await response.json();
            startSearchResults = data;

            if (data.length === 0) {
                resultsDiv.innerHTML = '<div class="text-center py-3 t-text-muted text-sm">未找到相关地点</div>';
                return;
            }

            resultsDiv.innerHTML = data.map((item, idx) => `
                <div onclick="pickStartLocation(${idx})" class="px-4 py-2.5 cursor-pointer transition flex items-center gap-3" style="border-bottom: 1px solid var(--border-subtle);">
                    <i class="fas fa-map-pin t-text-muted flex-shrink-0"></i>
                    <div class="min-w-0">
                        <div class="font-medium text-sm t-text truncate">${item.name}</div>
                        <div class="text-xs t-text-muted truncate">${item.district || ''} ${item.address || ''}</div>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            console.error(e);
            resultsDiv.innerHTML = '<div class="text-center py-3 text-red-400 text-sm">搜索出错</div>';
        }
    }, 400);
}

function pickStartLocation(index) {
    const item = startSearchResults[index];
    selectedStartLocation = {
        name: item.name,
        address: item.address,
        city: item.city || item.district || '',
        lat: item.location ? parseFloat(item.location.split(',')[1]) : null,
        lng: item.location ? parseFloat(item.location.split(',')[0]) : null
    };

    // Update UI: show selected badge, hide input
    const addrHint = item.district || item.address || '';
    document.getElementById('start-location-name').textContent = addrHint ? `${item.name}（${addrHint}）` : item.name;
    document.getElementById('start-location-selected').classList.remove('hidden');
    document.getElementById('start-location-results').classList.add('hidden');
    document.getElementById('create-start-input-wrap').classList.add('hidden');
}

function clearStartLocation() {
    selectedStartLocation = null;
    document.getElementById('start-location-selected').classList.add('hidden');
    document.getElementById('create-start-input-wrap').classList.remove('hidden');
    document.getElementById('create-start-location').value = '';
    document.getElementById('start-location-results').classList.add('hidden');
}

async function createNewPlan() {
    document.getElementById('create-date').valueAsDate = new Date();
    document.getElementById('create-days').value = 1;
    clearStartLocation(); // Reset start location state
    showView('create-plan');
}

async function submitCreatePlan() {
    // Validate starting point
    if (!selectedStartLocation) {
        showToast('请先搜索并选择出发起点', 'error');
        document.getElementById('create-start-location').focus();
        return;
    }

    const startDateStr = document.getElementById('create-date').value;
    const totalDays = parseInt(document.getElementById('create-days').value) || 1;

    // Show loading
    const saveBtn = document.querySelector('button[onclick="submitCreatePlan()"]');
    const originalContent = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 创建中...';

    // Auto-generate title
    const dateStr = new Date(startDateStr).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
    const cityName = selectedStartLocation.city || '';
    const title = cityName ? `${cityName} · ${dateStr}出发 · ${totalDays}日旅行` : `${dateStr}出发 · ${totalDays}日旅行`;

    // Build Days
    const days = [];
    let currentDate = new Date(startDateStr);

    for (let i = 0; i < totalDays; i++) {
        days.push({
            day_index: i + 1,
            date: currentDate.toISOString().split('T')[0],
            city: selectedStartLocation.city || '',
            segments: []
        });
        currentDate.setDate(currentDate.getDate() + 1);
    }

    const newPlan = {
        title: title,
        days: days,
        start_location: {
            name: selectedStartLocation.name,
            lat: selectedStartLocation.lat,
            lng: selectedStartLocation.lng,
            address: selectedStartLocation.address,
            city: selectedStartLocation.city
        }
    };

    try {
        const response = await fetch('/travel/plans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newPlan)
        });
        
        if (response.ok) {
            const plan = await response.json();
            showToast('行程创建成功');
            activePlan = plan;
            
            if (!activePlan.days) activePlan.days = [];

            // Set the selected starting point as the first location
            activePlan.tempStartLocation = selectedStartLocation;
            
            showView('plan-detail');
            renderPlanDetail();
        } else {
            showToast('创建失败', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('创建出错', 'error');
    } finally {
        saveBtn.innerHTML = originalContent;
        saveBtn.disabled = false;
    }
}

// --- Plan Detail Editor Logic ---

let activePlan = null;
let activeDetailTab = 0;  // 'overview' | 0-based 第几天，0=第1天
let editingSegmentIndex = -1;
/** 当前查看详情的交通段索引，用于详情弹窗内「更改交通方式」 */
let viewingDetailSegmentIndex = -1;
/** 非 null 时表示在指定地点索引前插入新地点（即作为该索引前一站的下一站）；null 表示追加到末尾 */
let insertAtIndex = null;
let debounceTimer = null;

/** 当前选中的是第几天（用于添加/编辑 segment），总览时默认第 1 天 */
function getCurrentDayIndex() {
    return activeDetailTab === 'overview' ? 0 : activeDetailTab;
}

function setPlanDayTab(tabValue) {
    activeDetailTab = tabValue;
    renderPlanDetail();
}

/** 根据出发日期、天数、起点等同步更新行程标题（格式：地点 · X月X日出发 · N日旅行） */
function syncPlanTitleFromMeta() {
    if (!activePlan || !activePlan.days.length) return;
    const locationPart = (activePlan.start_location && activePlan.start_location.name)
        ? activePlan.start_location.name
        : (activePlan.title && activePlan.title.includes(' · '))
            ? activePlan.title.split(' · ')[0].trim()
            : '';
    const dateStr = activePlan.days[0].date
        ? new Date(activePlan.days[0].date).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
        : '';
    const dayCount = activePlan.days.length;
    activePlan.title = locationPart
        ? `${locationPart} · ${dateStr}出发 · ${dayCount}日旅行`
        : `${dateStr}出发 · ${dayCount}日旅行`;
}

/** 修改出发日期：重算所有天的 date，并同步标题 */
function updatePlanDepartureDate(dateStr) {
    if (!activePlan || !dateStr || !activePlan.days.length) return;
    const start = new Date(dateStr);
    activePlan.days.forEach((day, i) => {
        const d = new Date(start);
        d.setDate(d.getDate() + i);
        day.date = d.toISOString().split('T')[0];
    });
    syncPlanTitleFromMeta();
    renderPlanDetail();
}

/** 修改当日出发时间（仅当前选中的天） */
function updateDayStartTime(hm) {
    if (!activePlan || !hm) return;
    const dayIndex = getCurrentDayIndex();
    if (activeDetailTab === 'overview' || dayIndex >= activePlan.days.length) return;
    activePlan.days[dayIndex].start_time_hm = hm;
    renderPlanDetail();
    saveActivePlanSilently();
}

/** 修改旅游天数：增删末尾的天 */
function updatePlanDaysCount(newCount) {
    if (!activePlan || newCount < 1 || newCount > 30) return;
    const current = activePlan.days.length;
    if (newCount === current) return;

    if (newCount < current) {
        const toRemove = activePlan.days.slice(newCount);
        const hasContent = toRemove.some(d => (d.segments && d.segments.length > 0));
        if (hasContent && !confirm(`将删除第 ${newCount + 1}～${current} 天的行程内容，确定继续？`)) {
            document.getElementById('detail-total-days').value = current;
            return;
        }
        activePlan.days.length = newCount;
        if (activeDetailTab !== 'overview' && activeDetailTab >= newCount) {
            activeDetailTab = newCount - 1;
        }
    } else {
        const lastDate = activePlan.days[activePlan.days.length - 1].date;
        const base = lastDate ? new Date(lastDate) : new Date();
        for (let i = current; i < newCount; i++) {
            const d = new Date(base);
            d.setDate(d.getDate() + (i - current + 1));
            activePlan.days.push({
                day_index: i + 1,
                date: d.toISOString().split('T')[0],
                city: activePlan.days[0].city || '',
                segments: [],
                start_time_hm: '08:00'
            });
        }
    }
    syncPlanTitleFromMeta();
    renderPlanDetail();
}

async function viewPlan(planId) {
    try {
        const response = await fetch(`/travel/plans/${planId}`);
        if (!response.ok) throw new Error('Failed to load plan');
        
        activePlan = await response.json();
        
        // Ensure data structure integrity
        if (!activePlan.days) activePlan.days = [];
        if (activePlan.days.length === 0) activePlan.days.push({ day_index: 1, segments: [] });
        activePlan.days.forEach(d => { if (!d.segments) d.segments = []; });
        
        activeDetailTab = 0;  // 默认选中第 1 天
        showView('plan-detail');
        renderPlanDetail();
    } catch (error) {
        console.error(error);
        alert('无法加载行程详情');
    }
}

function renderPlanDetail() {
    // Fix: Recalculate duration from times if present (especially for imported tickets with full dates)
    if (activePlan && activePlan.days) {
        activePlan.days.forEach(day => {
            (day.segments || []).forEach(seg => {
                 const dep = seg.details?.departure_time || seg.origin?.departure_time;
                 const arr = seg.details?.arrival_time || seg.destination?.arrival_time;
                 if (dep && arr) {
                     const sec = durationSecondsFromTimes(dep, arr);
                     if (sec > 0) {
                         seg.duration_minutes = sec / 60;
                     } else {
                         // Try HH:MM cross-day
                         if (/^\d{1,2}:\d{2}$/.test(dep.trim()) && /^\d{1,2}:\d{2}$/.test(arr.trim())) {
                             const depMin = hmToMinutes(dep);
                             const arrMin = hmToMinutes(arr);
                             let diff = arrMin - depMin;
                             if (diff < 0) diff += 24 * 60;
                             if (diff > 0) seg.duration_minutes = diff;
                         }
                     }
                 }
            });
        });
    }

    const titleEl = document.getElementById('detail-title');
    const subtitleEl = document.getElementById('detail-subtitle');
    const tabsWrap = document.getElementById('plan-day-tabs');
    const timelineEl = document.getElementById('plan-timeline');
    
    titleEl.textContent = activePlan.title || '未命名行程';
    const dayCount = activePlan.days.length;
    const spotCount = activePlan.days.reduce((acc, day) => {
        return acc + (day.segments.length > 0 ? day.segments.length + 1 : 0);
    }, 0);
    subtitleEl.textContent = `${dayCount} 天 · ${spotCount} 个地点`;

    // 同步出发日期、旅游天数、当日出发时间控件
    const departureInput = document.getElementById('detail-departure-date');
    const daysInput = document.getElementById('detail-total-days');
    const startTimeWrap = document.getElementById('detail-day-start-time-wrap');
    const startTimeInput = document.getElementById('detail-day-start-time');
    if (departureInput && activePlan.days[0].date) departureInput.value = activePlan.days[0].date;
    if (daysInput) daysInput.value = activePlan.days.length;
    const isDayTab = typeof activeDetailTab === 'number';
    if (startTimeWrap) startTimeWrap.classList.toggle('hidden', !isDayTab);
    if (startTimeInput && isDayTab && activePlan.days[activeDetailTab]) {
        const day = activePlan.days[activeDetailTab];
        startTimeInput.value = day.start_time_hm || '08:00';
    }

    // 渲染日期 Tab 栏：总览、第1天、第2天...
    const tabValues = ['overview', ...activePlan.days.map((_, i) => i)];
    const tabLabels = ['总览', ...activePlan.days.map((d, i) => `第 ${i + 1} 天`)];
    let tabsHtml = '';
    tabValues.forEach((val, i) => {
        const isActive = activeDetailTab === val;
        const label = tabLabels[i];
        tabsHtml += `<button type="button" onclick="setPlanDayTab(${val === 'overview' ? "'overview'" : val})"
            class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition whitespace-nowrap
            ${isActive ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20' : 't-text-sub'}"
            style="${isActive ? '' : 'background: var(--bg-card); border: 1px solid var(--border-color);'}">${label}</button>`;
    });
    tabsWrap.innerHTML = tabsHtml;

    // 总览：展示每天摘要
    if (activeDetailTab === 'overview') {
        let overviewHtml = '<div class="space-y-4">';
        activePlan.days.forEach((day, dayIdx) => {
            const segs = day.segments || [];
            const count = segs.length > 0 ? segs.length + 1 : 0;
            const dateStr = day.date ? new Date(day.date).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' }) : `第 ${dayIdx + 1} 天`;
            overviewHtml += `
                <div onclick="setPlanDayTab(${dayIdx})" class="rounded-xl p-4 cursor-pointer transition group" style="background: var(--bg-card); border: 1px solid var(--border-color);">
                    <div class="flex justify-between items-center">
                        <span class="font-bold t-text group-hover:text-cyan-500 transition">第 ${dayIdx + 1} 天</span>
                        <span class="text-sm t-text-muted">${dateStr}</span>
                    </div>
                    <p class="text-sm t-text-sub mt-1">${count} 个地点</p>
                </div>`;
        });
        overviewHtml += '</div>';
        timelineEl.innerHTML = overviewHtml;
        return;
    }

    // 单日时间线
    const dayIndex = activeDetailTab;
    const day = activePlan.days[dayIndex];
    const segments = day.segments;
    
    if (segments.length === 0) {
        ensureDayStayArray(day);
        const arrivalTimes = getDayArrivalTimes(day);
        const at0 = arrivalTimes[0];
        const startLocation = (dayIndex === 0) ? (activePlan.start_location || activePlan.tempStartLocation) : null;
        
        const cardHtml = startLocation 
            ? renderLocationCard(startLocation, 0, true, dayIndex === 0 ? '起点' : null, at0 ? at0.arrivalHm : (day.start_time_hm || '08:00'), at0 ? at0.stayMinutes : 0, dayIndex, at0 ? at0.departureHm : null)
            : renderLocationCard(null, 0, true, null, at0 ? at0.arrivalHm : (day.start_time_hm || '08:00'), at0 ? at0.stayMinutes : 0, dayIndex, at0 ? at0.departureHm : null);

        timelineEl.innerHTML = `
            <div class="relative pb-12">
                <div class="timeline-line h-full"></div>
                <div class="relative z-10 space-y-2">
                    ${cardHtml}
                    <!-- Add Location Card Removed -->
                </div>
            </div>
        `;
        return;
    }

    ensureDayStayArray(day);
    const arrivalTimes = getDayArrivalTimes(day);

    // --- Mobile View (Existing Linear Layout) ---
    let mobileHtml = `<div class="md:hidden relative pb-12">
        <div class="timeline-line h-full" style="left: 24px; position: absolute; top: 0; bottom: 0; width: 2px; background: var(--timeline-line-color); z-index: 0;"></div>
        <div class="relative z-10">`;
        
    segments.forEach((seg, index) => {
        const isFirst = index === 0;
        const isLastSeg = index === segments.length - 1;
        const at0 = arrivalTimes[index];
        
        // Use standard linear card for mobile
        mobileHtml += renderLocationCard(seg.origin, index, false, isFirst && dayIndex === 0 ? '起点' : null, at0 ? at0.arrivalHm : '--', at0 ? at0.stayMinutes : 0, dayIndex, at0 ? at0.departureHm : null);
        mobileHtml += renderTransportConnector(seg, index);
        
        if (isLastSeg) {
            const at1 = arrivalTimes[index + 1];
            mobileHtml += renderLocationCard(seg.destination, index + 1, true, '终点', at1 ? at1.arrivalHm : '--', at1 ? at1.stayMinutes : 0, dayIndex, at1 ? at1.departureHm : null);
        }
    });
    
    // Add "Plus" button for mobile (Removed per user request)
    // mobileHtml += `...`;
    
    mobileHtml += `</div></div>`;

    // --- Desktop View (Canvas / Free Layout) ---
    // Calculate layout if missing
    ensureLayoutCoordinates(dayIndex);
    const layout = day.layout || [];

    // Ensure container has height
    // Find max Y to set container height
    let maxY = 600;
    layout.forEach(p => {
        if (p && p.y + 200 > maxY) maxY = p.y + 200;
    });
    
    let desktopHtml = `<div class="hidden md:block snake-container" id="snake-container-${dayIndex}" style="height: ${maxY}px; position: relative;">
        <svg class="snake-svg-container" id="snake-svg-${dayIndex}" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index: 0; pointer-events:none;"></svg>
    `;

    // Render all location items (absolute positioning)
    segments.forEach((seg, i) => {
        const pos = layout[i] || {x: 0, y: 0};
        desktopHtml += renderCanvasItem(seg.origin, i, false, (i===0 && dayIndex===0) ? '起点' : null, arrivalTimes[i], dayIndex, pos);
    });
    
    // Last destination
    const lastSegIdx = segments.length - 1;
    if (lastSegIdx >= 0) {
        const i = segments.length;
        const pos = layout[i] || {x: 0, y: 0};
        desktopHtml += renderCanvasItem(segments[lastSegIdx].destination, i, true, '终点', arrivalTimes[i], dayIndex, pos);
    }

    // Add Button (Removed per user request)
    // const addBtnIdx = segments.length + (lastSegIdx >= 0 ? 1 : (segments.length === 0 ? 0 : 1));
    // const nodeCount = segments.length + 1;
    // const addBtnPos = layout[nodeCount] || {x: 50, y: 50};
    // desktopHtml += `...`;

    desktopHtml += `</div>`;

    timelineEl.innerHTML = mobileHtml + desktopHtml;
    
    // Trigger Line Drawing
    setTimeout(() => drawCanvasConnections(dayIndex), 50);
    // Remove old snakeResizeHandler logic if needed, or update it
    if (!window.snakeResizeHandler) {
        window.snakeResizeHandler = true;
        window.addEventListener('resize', () => {
             const activeIdx = typeof activeDetailTab === 'number' ? activeDetailTab : 0;
             drawCanvasConnections(activeIdx);
        });
    }

    // ... (rest of function)

    // 航班/火车段若未手动导入距离与耗时，则用高德补全
    // 使用标记避免对同一段重复请求（失败后不再重试，直到用户手动触发）
    const needAmap = [];
    segments.forEach((seg, i) => {
        if ((seg.type === 'flight' || seg.type === 'train') &&
            (seg.duration_minutes == null || seg.distance_km == null || seg.duration_minutes === 0 || seg.distance_km === 0) &&
            !seg._amapAttempted) {
            needAmap.push(i);
        }
    });
    if (needAmap.length > 0) {
        (async () => {
            let anyUpdated = false;
            for (const i of needAmap) {
                segments[i]._amapAttempted = true;  // 标记已尝试，避免重复请求
                try {
                    const updated = await ensureSegmentFromAmap(dayIndex, i);
                    if (updated) anyUpdated = true;
                } catch (_) {}
                await new Promise(r => setTimeout(r, 400));
            }
            if (anyUpdated) {
                renderPlanDetail();
                // 补全成功后自动保存，下次从行程列表进入无需再请求高德
                saveActivePlanSilently();
            }
        })();
    }
}

/** 航班/火车段缺少距离或耗时时，请求高德并回写；返回是否更新了 segment */
async function ensureSegmentFromAmap(dayIndex, segmentIndex) {
    const segment = activePlan?.days?.[dayIndex]?.segments?.[segmentIndex];
    if (!segment || (segment.type !== 'flight' && segment.type !== 'train')) return false;
    if (segment.origin?.name && segment.destination?.name &&
        segment.duration_minutes != null && segment.distance_km != null &&
        segment.duration_minutes > 0 && segment.distance_km > 0) {
        return false;
    }
    try {
        const result = await calculateSegmentData(segment.origin, segment.destination, segment.type);
        if (result.distance_km != null) segment.distance_km = result.distance_km;
        if (result.duration_minutes != null) segment.duration_minutes = result.duration_minutes;
        return true;
    } catch (e) {
        // 距离过短时后端会拒接火车/航班（如「两地直线距离仅 X 公里，不适合使用火车/高铁」），改用公交/地铁估算
        if (segment.type === 'train' || segment.type === 'flight') {
            try {
                const fallback = await calculateSegmentData(segment.origin, segment.destination, 'transit');
                if (fallback.distance_km != null) segment.distance_km = fallback.distance_km;
                if (fallback.duration_minutes != null) segment.duration_minutes = fallback.duration_minutes;
                return true;
            } catch (_) {}
        }
        return false;
    }
}

function renderLocationCard(location, index, isLast = false, roleLabel = null, arrivalHm = '--', stayMinutes = 0, dayIndex = 0, departureHm = null) {
    const safeLoc = location || {};
    const name = safeLoc.name || (roleLabel === '起点' ? '起点（待补充）' : roleLabel === '终点' ? '终点（待补充）' : '未知地点');
    const address = safeLoc.address || safeLoc.city || safeLoc.name || '未知地址';
    const stayVal = Math.max(0, parseInt(stayMinutes, 10) || 0);
    const timeLabel = departureHm && stayVal > 0 ? `到达 ${arrivalHm} · 离开 ${departureHm}` : `到达 ${arrivalHm}`;
    
    // Status/Role Badge
    let statusBadge = '';
    if (roleLabel === '起点') statusBadge = '<span class="px-2 py-0.5 rounded-full text-xs font-bold shadow-sm" style="background: var(--badge-start-bg); color: var(--badge-start-text);">起点</span>';
    else if (roleLabel === '终点') statusBadge = '<span class="px-2 py-0.5 rounded-full text-xs font-bold shadow-sm" style="background: var(--badge-end-bg); color: var(--badge-end-text);">终点</span>';

    return `
        <div class="flex gap-4 items-stretch mb-2 group relative">
            <!-- Timeline Node -->
            <div class="flex flex-col items-center flex-shrink-0 w-12 pt-2">
                <div class="timeline-node ${roleLabel === '起点' ? 'bg-emerald-500 border-emerald-300 text-white' : (isLast ? 'bg-rose-500 border-rose-300 text-white' : '')}">
                    <span class="text-sm font-bold font-mono">${index + 1}</span>
                </div>
                <div class="mt-2 text-[10px] t-text-muted font-mono font-medium tracking-tight px-1 rounded" style="background: var(--bg-surface);">
                    ${arrivalHm}
                </div>
            </div>

            <!-- Card Content -->
            <div class="flex-1 min-w-0">
                <div class="location-card ${roleLabel === '起点' ? 'is-start' : (roleLabel === '终点' ? 'is-end' : '')}">
                    <div class="flex justify-between items-start gap-3">
                        <div class="min-w-0 flex-1">
                            <div class="flex items-center flex-wrap gap-2 mb-1">
                                <h4 class="font-bold t-heading text-lg leading-snug">${name}</h4>
                                ${statusBadge}
                            </div>
                            
                            <p class="text-sm t-text-sub flex items-center gap-1.5 mb-3">
                                <i class="fas fa-map-marker-alt t-text-muted text-xs"></i>
                                <span class="truncate opacity-80">${address}</span>
                            </p>

                            <div class="flex items-center gap-4 flex-wrap">
                                <div class="inline-flex items-center gap-2 rounded-lg px-2 py-1" style="background: var(--bg-inset); border: 1px solid var(--border-subtle);">
                                    <i class="far fa-clock t-text-muted text-xs"></i>
                                    <span class="text-xs t-text-sub font-medium">${timeLabel}</span>
                                </div>

                                <div class="flex items-center gap-1.5" onclick="event.stopPropagation()">
                                    <i class="fas fa-hourglass-half t-text-muted text-xs"></i>
                                    <span class="text-xs t-text-muted">停留</span>
                                    <input type="number" min="0" max="480" step="15" value="${stayVal}" 
                                        class="w-12 text-xs text-center border-0 bg-transparent py-0.5 focus:ring-0 font-medium transition-colors" style="border-bottom: 1px solid var(--border-color); color: var(--text-primary);"
                                        onchange="setLocationStayMinutes(${dayIndex}, ${index}, this.value)">
                                    <span class="text-xs t-text-muted">分</span>
                                </div>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="flex flex-col gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200" onclick="event.stopPropagation()">
                            <button type="button" class="w-8 h-8 flex items-center justify-center rounded-lg text-cyan-600 hover:bg-cyan-500 hover:text-white transition shadow-sm" style="background: var(--nav-active-bg);" onclick="showAddLocationModal(${isLast ? 'null' : index + 1})" title="在此处插入下一站">
                                <i class="fas fa-plus text-xs"></i>
                            </button>
                            <button type="button" class="w-8 h-8 flex items-center justify-center rounded-lg t-text-muted hover:bg-rose-500/10 hover:text-rose-500 transition shadow-sm" style="background: var(--bg-inset);" onclick="removeLocation(${index}, ${isLast})" title="删除此地点">
                                <i class="fas fa-trash-alt text-xs"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function setLocationStayMinutes(dayIndex, locationIndex, value) {
    const day = activePlan?.days?.[dayIndex];
    if (!day) return;
    ensureDayStayArray(day);
    const mins = Math.max(0, Math.min(480, parseInt(value, 10) || 0));
    if (day.location_stay_minutes[locationIndex] !== mins) {
        day.location_stay_minutes[locationIndex] = mins;
        renderPlanDetail();
        saveActivePlanSilently();
    }
}

function renderTransportConnector(segment, index) {
    const duration = segment.duration_minutes ? formatDuration(segment.duration_minutes * 60) : '--';
    const distance = segment.distance_km ? `${segment.distance_km}km` : '--';
    const dep = segment.details?.departure_time || segment.origin?.departure_time;
    const arr = segment.details?.arrival_time || segment.destination?.arrival_time;
    const timeRange = (dep && arr) ? `${dep} → ${arr}` : (dep || arr || '');
    const isFlightOrTrain = segment.type === 'flight' || segment.type === 'train';
    
    let infoText;
    if (isFlightOrTrain && timeRange) {
        infoText = timeRange; // For badges, keep it short. Detailed info in modal.
    } else {
        infoText = duration;
    }

    let icon = 'fa-car';
    let label = '驾车';
    if (segment.type === 'transit') {
        icon = 'fa-bus';
        label = (segment.details && segment.details.display_label === '城际交通') ? '城际交通' : '公交';
    }
    if (segment.type === 'walking') { icon = 'fa-walking'; label = '步行'; }
    if (segment.type === 'cycling') { icon = 'fa-bicycle'; label = '骑行'; }
    if (segment.type === 'flight') { icon = 'fa-plane'; label = segment.details?.flight_no || '航班'; }
    if (segment.type === 'train') { icon = 'fa-train'; label = segment.details?.train_no || '高铁'; }

    return `
        <div class="mb-2 pl-12">
            <div onclick="openTransportDetailModal(${index})" class="transport-badge group/conn" title="点击查看详情">
                <i class="fas ${icon} text-xs opacity-70"></i>
                <span>${label}</span>
                <span class="w-px h-3 bg-cyan-200/50 mx-1"></span>
                <span class="font-mono text-[10px] opacity-80">${infoText}</span>
                <span class="font-mono text-[10px] opacity-60 ml-1">(${distance})</span>
                <i class="fas fa-chevron-right text-[10px] opacity-40 ml-1 group-hover/conn:opacity-100 transition-opacity"></i>
            </div>
        </div>
    `;
}

// ---------------------------------------------------------
// Free Layout & Canvas Dragging Logic
// ---------------------------------------------------------

/**
 * 确保当前天有布局坐标数据。
 * 如果没有，基于原来的 Snake Flow 算法生成默认坐标。
 */
function ensureLayoutCoordinates(dayIndex) {
    const day = activePlan.days[dayIndex];
    if (!day) return;
    
    // 节点数量 = segments.length + 1 (起点 + 所有终点) + 1 (添加按钮)
    // 但我们的数据结构里 segments 存储的是段。
    // 节点 0 = seg[0].origin
    // 节点 1 = seg[0].destination
    // ...
    // 实际上我们之前把它们拍平成 allItems 数组。
    
    const segments = day.segments || [];
    const nodeCount = segments.length + 1; // Locations only
    
    // 如果已经有布局且长度足够，直接返回
    if (day.layout && day.layout.length >= nodeCount) return;
    
    // 初始化布局数组
    if (!day.layout) day.layout = [];
    
    // 默认参数
    const COLUMNS = 3;
    const X_GAP = 300; // 水平间距
    const Y_GAP = 200; // 垂直间距
    const START_X = 50;
    const START_Y = 50;
    
    for (let i = 0; i < nodeCount; i++) {
        // 如果该节点已有坐标，保留
        if (day.layout[i]) continue;
        
        const row = Math.floor(i / COLUMNS);
        const col = i % COLUMNS;
        const isReverseRow = row % 2 !== 0;
        
        // 计算蛇形布局坐标
        const effectiveCol = isReverseRow ? (COLUMNS - 1 - col) : col;
        
        day.layout[i] = {
            x: START_X + effectiveCol * X_GAP,
            y: START_Y + row * Y_GAP
        };
    }
    
    // 添加按钮的坐标 (在最后一个节点之后)
    if (!day.layout[nodeCount]) {
         const i = nodeCount;
         const row = Math.floor(i / COLUMNS);
         const col = i % COLUMNS;
         const isReverseRow = row % 2 !== 0;
         const effectiveCol = isReverseRow ? (COLUMNS - 1 - col) : col;
         day.layout[nodeCount] = {
            x: START_X + effectiveCol * X_GAP,
            y: START_Y + row * Y_GAP
         };
    }
}

// 自由拖拽状态
let freeDragState = {
    isDragging: false,
    dayIndex: null,
    nodeIndex: null, // 对应 layout 数组的索引
    startX: 0,
    startY: 0,
    initialLeft: 0,
    initialTop: 0,
    el: null
};

function initFreeDrag(e, dayIndex, nodeIndex) {
    if (e.button !== 0) return; // 仅左键
    e.preventDefault(); // 阻止默认文本选择
    
    const el = document.getElementById(`snake-item-${dayIndex}-${nodeIndex}`);
    if (!el) return;

    freeDragState = {
        isDragging: true,
        dayIndex,
        nodeIndex,
        startX: e.clientX,
        startY: e.clientY,
        initialLeft: parseFloat(el.style.left) || 0,
        initialTop: parseFloat(el.style.top) || 0,
        el
    };
    
    el.style.zIndex = 100;
    el.style.cursor = 'grabbing';
    el.classList.add('shadow-2xl', 'scale-105');
    
    document.addEventListener('mousemove', handleFreeMouseMove);
    document.addEventListener('mouseup', handleFreeMouseUp);
}

function handleFreeMouseMove(e) {
    if (!freeDragState.isDragging) return;
    
    const dx = e.clientX - freeDragState.startX;
    const dy = e.clientY - freeDragState.startY;
    
    const newLeft = freeDragState.initialLeft + dx;
    const newTop = freeDragState.initialTop + dy;
    
    freeDragState.el.style.left = `${newLeft}px`;
    freeDragState.el.style.top = `${newTop}px`;
    
    // 实时更新连线
    requestAnimationFrame(() => {
        const day = activePlan.days[freeDragState.dayIndex];
        // 临时更新数据中的坐标以便连线计算使用（但不保存）
        if (day.layout && day.layout[freeDragState.nodeIndex]) {
            day.layout[freeDragState.nodeIndex].x = newLeft;
            day.layout[freeDragState.nodeIndex].y = newTop;
        }
        drawCanvasConnections(freeDragState.dayIndex);
    });
}

function handleFreeMouseUp(e) {
    if (!freeDragState.isDragging) return;
    
    const { dayIndex, nodeIndex, el } = freeDragState;
    
    // 保存最终坐标
    const day = activePlan.days[dayIndex];
    if (!day.layout) day.layout = [];
    
    const finalLeft = parseFloat(el.style.left);
    const finalTop = parseFloat(el.style.top);
    
    day.layout[nodeIndex] = {
        x: finalLeft,
        y: finalTop
    };
    
    // 调整容器高度以适应拖动（如果拖到了底部下面）
    const container = document.getElementById(`snake-container-${dayIndex}`);
    if (container) {
        const currentHeight = container.offsetHeight;
        if (finalTop + 200 > currentHeight) {
            container.style.height = `${finalTop + 300}px`;
        }
    }

    // 恢复样式
    el.style.zIndex = '';
    el.style.cursor = 'grab';
    el.classList.remove('shadow-2xl', 'scale-105');
    
    // 清理事件
    document.removeEventListener('mousemove', handleFreeMouseMove);
    document.removeEventListener('mouseup', handleFreeMouseUp);
    
    freeDragState.isDragging = false;
    freeDragState.el = null;
    
    saveActivePlanSilently();
}

/**
 * 画板模式下的连线绘制
 * 直接连接各个绝对定位的节点
 */
function drawCanvasConnections(dayIndex) {
    const container = document.getElementById(`snake-container-${dayIndex}`);
    if (!container) return;
    
    const svg = document.getElementById(`snake-svg-${dayIndex}`);
    if (!svg) return;
    
    const day = activePlan.days[dayIndex];
    const segments = day.segments || [];
    const layout = day.layout || [];
    
    // 清空旧线
    svg.innerHTML = '';
    container.querySelectorAll('.snake-transport').forEach(el => el.remove());

    // 定义箭头 Marker
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = `
        <marker id="arrowhead-${dayIndex}" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--snake-path-stroke)" />
        </marker>
    `;
    svg.appendChild(defs);

    // 遍历 Segments 画线
    // Segment i 连接 Node i (Origin) 和 Node i+1 (Destination)
    
    for (let i = 0; i < segments.length; i++) {
        const p1 = layout[i];
        const p2 = layout[i+1];
        
        if (!p1 || !p2) continue;
        
        // 节点尺寸假设 (需要与 CSS 匹配)
        // snake-item 宽度约 250px-300px? 不，现在是绝对定位，宽度取决于内容。
        // 我们假设连接的是中心点或者边缘。
        // 为了简单，我们先获取 DOM 元素的实际位置（如果已渲染），
        // 但为了性能，直接使用 layout 坐标作为左上角，并加上预估的中心偏移。
        
        // 假设卡片宽度 260px，高度 120px (估算)
        const CARD_W = 260;
        const CARD_H = 100; // 头部+内容
        
        const start = { x: p1.x + CARD_W / 2, y: p1.y + CARD_H / 2 };
        const end = { x: p2.x + CARD_W / 2, y: p2.y + CARD_H / 2 };
        
        // 画贝塞尔曲线
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('class', 'snake-path-segment');
        path.setAttribute('marker-end', `url(#arrowhead-${dayIndex})`);
        
        // 计算控制点 - 简单的水平/垂直 50% 混合
        const dist = Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2));
        const controlDist = Math.min(dist * 0.5, 150);
        
        // 简单的逻辑：如果 p2 在 p1 右侧，由右出由左入
        // 这里简化为：总是从中心连线，不考虑具体的出入口，SVG层在下层。
        
        // 尝试优化：从最近的边缘连线？
        // 保持简单：中心对中心，但 path 只画边缘外面的部分？
        // 不，Snake Flow 风格是线条在底层，所以中心对中心没问题，只是会被卡片遮住。
        
        const pathD = `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
        // 如果想平滑一点：
        // const pathD = `M ${start.x} ${start.y} Q ${(start.x+end.x)/2} ${(start.y+end.y)/2 - 20} ${end.x} ${end.y}`;
        
        path.setAttribute('d', pathD);
        svg.appendChild(path);
        
        // 渲染交通徽章 (在连线中点)
        const badgePos = {
            x: (start.x + end.x) / 2,
            y: (start.y + end.y) / 2
        };
        renderSnakeBadge(container, badgePos, i, segments[i]);
    }
}

// ---------------------------------------------------------
// End Free Layout Logic
// ---------------------------------------------------------

// Drag & Drop State
let dragSrcDayIndex = null;
let dragSrcItemIndex = null;

function handleDragStart(e, dayIndex, itemIndex) {
    dragSrcDayIndex = dayIndex;
    dragSrcItemIndex = itemIndex;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', itemIndex); // For Firefox
    
    // Add grabbing style
    e.target.closest('.snake-item').style.cursor = 'grabbing';
    e.target.closest('.snake-item').style.opacity = '0.4';
}

function handleDragEnd(e) {
    e.target.closest('.snake-item').style.opacity = '1';
    document.querySelectorAll('.snake-item').forEach(el => el.classList.remove('drag-over'));
    dragSrcDayIndex = null;
    dragSrcItemIndex = null;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    const target = e.target.closest('.snake-item');
    if (target && !target.classList.contains('drag-over')) {
        document.querySelectorAll('.snake-item').forEach(el => el.classList.remove('drag-over'));
        target.classList.add('drag-over');
    }
    return false;
}

function handleDragLeave(e) {
    const target = e.target.closest('.snake-item');
    if (target) {
        target.classList.remove('drag-over');
    }
}

async function handleDrop(e, dayIndex, targetIndex) {
    if (e.stopPropagation) e.stopPropagation();
    
    // Remove visual cues
    handleDragEnd(e);

    // Validate drop
    if (dragSrcDayIndex === null || dragSrcDayIndex !== dayIndex) return false;
    if (dragSrcItemIndex === targetIndex) return false;

    await reorderLocations(dayIndex, dragSrcItemIndex, targetIndex);
    return false;
}

async function reorderLocations(dayIndex, fromIndex, toIndex) {
    const day = activePlan.days[dayIndex];
    const segments = day.segments;
    
    // 1. Extract all locations in order [Origin, Dest1, Dest2, ...]
    const locations = [];
    if (segments.length > 0) {
        locations.push(segments[0].origin);
        segments.forEach(seg => locations.push(seg.destination));
    } else if (activePlan.tempStartLocation) {
        // Can't reorder single item
        return; 
    }

    // 2. Reorder array
    if (fromIndex < 0 || fromIndex >= locations.length || toIndex < 0 || toIndex >= locations.length) return;
    
    const [movedItem] = locations.splice(fromIndex, 1);
    locations.splice(toIndex, 0, movedItem);

    // 2.1 Sync start location if modifying Day 1
    if (dayIndex === 0 && locations.length > 0) {
        activePlan.start_location = {
            name: locations[0].name,
            address: locations[0].address,
            city: locations[0].city,
            lat: locations[0].lat,
            lng: locations[0].lng
        };
        // Also ensure tempStartLocation is cleared as we rely on segments now
        activePlan.tempStartLocation = null;
    }

    // 3. Reorder stay minutes
    ensureDayStayArray(day);
    const [movedStay] = day.location_stay_minutes.splice(fromIndex, 1);
    day.location_stay_minutes.splice(toIndex, 0, movedStay);

    // 4. Create new segments structure (Optimistic UI)
    const newSegments = [];
    document.getElementById('plan-timeline').style.opacity = '0.5';

    try {
        for (let i = 0; i < locations.length - 1; i++) {
            const origin = locations[i];
            const dest = locations[i+1];
            
            newSegments.push({
                type: 'driving', // Reset to driving for simplicity
                origin: origin,
                destination: dest,
                distance_km: 0,
                duration_minutes: 0,
                details: {} 
            });
        }
        
        day.segments = newSegments;
        renderPlanDetail(); // Immediate render
        
        // 5. Async recalculate all segments
        // We do this sequentially or parallel? Parallel is faster.
        const promises = newSegments.map(seg => 
            calculateSegmentData(seg.origin, seg.destination, seg.type)
                .then(res => {
                    seg.distance_km = res.distance_km;
                    seg.duration_minutes = res.duration_minutes;
                })
                .catch(e => console.error(e))
        );
        
        await Promise.all(promises);
        renderPlanDetail(); // Final render with data
        saveActivePlanSilently();

    } catch (e) {
        console.error(e);
        alert('重排失败');
        // Reload to restore state
        viewPlan(activePlan.id);
    } finally {
        document.getElementById('plan-timeline').style.opacity = '1';
    }
}

// --- Snake Flow Layout Helpers ---

function renderCanvasItem(location, index, isLast, roleLabel, timeData, dayIndex, pos) {
    const safeLoc = location || {};
    const name = safeLoc.name || '未知地点';
    const address = safeLoc.address || safeLoc.city || '';
    const arrivalHm = timeData ? timeData.arrivalHm : '--';
    const departureHm = timeData ? timeData.departureHm : '--';
    const stayMinutes = timeData ? timeData.stayMinutes : 0;

    let roleClass = '';
    if (roleLabel === '起点') roleClass = 'is-start';
    if (roleLabel === '终点') roleClass = 'is-end';

    let roleIcon = `<span class="font-mono font-bold t-text-muted">${index + 1}</span>`;
    if (roleLabel === '起点') roleIcon = '<i class="fas fa-map-marker-alt text-emerald-500"></i>';
    if (roleLabel === '终点') roleIcon = '<i class="fas fa-flag-checkered text-rose-500"></i>';

    // Width fixed for absolute layout
    const width = 260;

    return `
    <div class="snake-item absolute transition-shadow duration-200" id="snake-item-${dayIndex}-${index}" 
         style="left: ${pos.x}px; top: ${pos.y}px; width: ${width}px; cursor: grab;"
         onmousedown="initFreeDrag(event, ${dayIndex}, ${index})">
        <div class="flow-card ${roleClass} h-full select-none">
            <!-- Top Actions -->
            <div class="absolute top-2 right-2 opacity-0 hover:opacity-100 transition-opacity z-20 flex gap-1">
                <button onmousedown="event.stopPropagation()" onclick="removeLocation(${index}, ${isLast})" class="w-6 h-6 rounded-full t-text-muted hover:bg-rose-500 hover:text-white flex items-center justify-center transition" style="background: var(--bg-elevated);" title="删除">
                    <i class="fas fa-times text-xs"></i>
                </button>
            </div>

            <div class="flow-card-header group/header">
                <!-- Move Handle Visual Cue -->
                <div class="mr-2 transition-colors flex items-center h-8" style="color: var(--flow-handle-text);">
                    <i class="fas fa-arrows-alt"></i>
                </div>
                <div class="flow-card-icon">
                    ${roleIcon}
                </div>
                <div class="min-w-0 flex-1">
                    <div class="flow-card-title truncate" title="${name}">${name}</div>
                    <div class="flow-card-meta truncate" title="${address}">${address}</div>
                </div>
            </div>
            
            <div class="flow-time-grid mt-2">
                 <div class="flow-time-item">
                    <div class="flow-time-label">到达</div>
                    <div class="flow-time-val">${arrivalHm}</div>
                 </div>
                 <div class="flow-time-item flex flex-col justify-center" title="点击修改停留" onmousedown="event.stopPropagation()">
                    <div class="flow-time-label">停留</div>
                    <div class="flex items-center justify-center rounded px-1" style="background: var(--flow-time-grid-bg);">
                        <input type="number" value="${stayMinutes}" min="0" step="15" 
                            class="flow-time-input"
                            onchange="setLocationStayMinutes(${dayIndex}, ${index}, this.value)">
                        <span class="text-[9px] t-text-muted font-medium">m</span>
                    </div>
                 </div>
                 <div class="flow-time-item">
                    <div class="flow-time-label">离开</div>
                    <div class="flow-time-val">${departureHm}</div>
                 </div>
            </div>
        </div>
    </div>
    `;
}

// Old Snake Lines Logic (Deprecated/Removed)
// The canvas line drawing is now handled by drawCanvasConnections above
function drawSnakeLines(dayIndex, segments) {
    // Legacy function stub to prevent errors if called by resize listeners
    // Now redirects to new canvas drawer
    drawCanvasConnections(dayIndex);
}

function renderSnakeBadge(container, pos, index, segment) {
    const badge = document.createElement('div');
    
    // Check if editable
    const isFixed = (segment.type === 'flight' && segment.details?.flight_no) || 
                    (segment.type === 'train' && segment.details?.train_no);
    
    const cursorClass = isFixed ? 'cursor-default' : 'cursor-pointer';
    
    badge.className = `snake-transport absolute z-30 flex items-center gap-2 px-3 py-1.5 text-xs rounded-full shadow-lg backdrop-blur-sm transition-all duration-200 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap group/badge ${cursorClass}`;
    badge.style.cssText += `background: var(--transport-bg); color: var(--transport-text); border: 1px solid var(--transport-border);`;
    
    badge.style.transform = 'translate(-50%, -50%)';
    
    // Data Preparation
    let icon = 'fa-car';
    let typeName = '驾车'; // Badge label (Generic)
    let detailTitle = '';  // Tooltip Header (Specific: Flight No, etc.)
    
    if (segment.type === 'transit') { icon = 'fa-bus'; typeName = '公交'; }
    if (segment.type === 'walking') { icon = 'fa-walking'; typeName = '步行'; }
    if (segment.type === 'cycling') { icon = 'fa-bicycle'; typeName = '骑行'; }
    if (segment.type === 'flight') { 
        icon = 'fa-plane'; 
        typeName = '航班'; 
        detailTitle = segment.details?.flight_no || '未知航班';
    }
    if (segment.type === 'train') { 
        icon = 'fa-train'; 
        typeName = '火车'; 
        detailTitle = segment.details?.train_no || '未知车次';
    }
    
    const dep = segment.details?.departure_time || segment.origin?.departure_time || '--:--';
    const arr = segment.details?.arrival_time || segment.destination?.arrival_time || '--:--';
    const hasTimes = (dep !== '--:--' && arr !== '--:--');

    // 优先根据起降时间计算时长（处理跨天）
    let displayDuration = segment.duration_minutes ? formatDuration(segment.duration_minutes * 60) : '--';
    
    if (hasTimes) {
        // 尝试计算精确时长（支持 "YYYY-MM-DD HH:MM" 及同日 "HH:MM"）
        const durationSec = durationSecondsFromTimes(dep, arr);
        if (durationSec > 0) {
            displayDuration = formatDuration(durationSec);
        } else {
            // 处理跨天 "HH:MM" (如 23:00 -> 01:00)
            const depMin = hmToMinutes(dep);
            const arrMin = hmToMinutes(arr);
            // 仅当确实是 HH:MM 格式时才应用跨天逻辑 (hmToMinutes 对日期字符串返回 0)
            const isSimpleTime = /^\d{1,2}:\d{2}$/.test(dep.trim()) && /^\d{1,2}:\d{2}$/.test(arr.trim());
            
            if (isSimpleTime) {
                let diffMin = arrMin - depMin;
                if (diffMin < 0) diffMin += 24 * 60; // 跨天处理：假设是次日到达
                
                if (diffMin > 0) {
                    displayDuration = formatDuration(diffMin * 60);
                }
            }
        }
    }

    // Fix: 驾车/步行等没有起降时间，duration 可能是 '--' 如果后端没算出来，
    // 但如果有 duration_minutes，上面已经赋值了。
    // 问题在于之前的 if (duration || ...) 判断可能被 displayDuration 覆盖逻辑影响。
    
    const distance = segment.distance_km ? `${segment.distance_km}km` : '--';
    
    // 1. Badge Content: Generic Type Only
    let html = `<i class="fas ${icon} ${isFixed ? 'opacity-70' : 'text-cyan-500'}"></i> <span class="font-bold">${typeName}</span>`;
    
    // 2. Tooltip Content (Rich & Aligned)
    // Show tooltip if we have ANY info: duration, distance, times, or specific title
    if ((displayDuration && displayDuration !== '--') || (distance && distance !== '--') || hasTimes || detailTitle) {
        let detailsHtml = '';
        
        // Header: Flight No / Type
        const headerText = detailTitle || typeName;
        detailsHtml += `
            <div class="flex items-center gap-2 pb-2 mb-2 border-b border-slate-600/50">
                <i class="fas ${icon} text-cyan-400"></i>
                <span class="font-bold text-white text-sm">${headerText}</span>
            </div>
        `;
        
        // Grid Content
        detailsHtml += `<div class="grid grid-cols-[16px_1fr] gap-y-2 gap-x-2 text-left items-start">`;
        
        // Row: Time (Split into two rows)
        if (hasTimes) {
            detailsHtml += `
                <div class="flex justify-center mt-0.5"><i class="fas fa-plane-departure text-slate-400 text-[10px]"></i></div>
                <div class="font-mono text-cyan-50 font-medium">${dep}</div>
                
                <div class="flex justify-center mt-0.5"><i class="fas fa-plane-arrival text-slate-400 text-[10px]"></i></div>
                <div class="font-mono text-cyan-50 font-medium">${arr}</div>
            `;
        }
        
        // Row: Duration
        if (displayDuration && displayDuration !== '--') {
            detailsHtml += `
                <div class="flex justify-center mt-0.5"><i class="fas fa-hourglass-half text-slate-400 text-[10px]"></i></div>
                <div class="text-slate-300">${displayDuration}</div>
            `;
        }
        
        // Row: Distance
        if (distance && distance !== '--') {
            detailsHtml += `
                <div class="flex justify-center mt-0.5"><i class="fas fa-ruler-horizontal text-slate-400 text-[10px]"></i></div>
                <div class="text-slate-300 font-mono">${distance}</div>
            `;
        }
        
        detailsHtml += `</div>`; // End Grid

        // Edit Hint
        if (!isFixed) {
            detailsHtml += `
                <div class="mt-3 pt-2 border-t border-slate-600/50 text-center">
                    <span class="text-[10px] text-cyan-500/80">点击切换方式</span>
                </div>
            `;
        }

        html += `
            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 min-w-[180px] bg-slate-800 p-4 rounded-xl border border-slate-600 shadow-2xl opacity-0 invisible group-hover/badge:opacity-100 group-hover/badge:visible transition-all duration-200 pointer-events-none z-50 flex flex-col scale-95 group-hover/badge:scale-100 origin-bottom">
                ${detailsHtml}
                <!-- Arrow -->
                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-slate-800"></div>
                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[7px] border-transparent border-t-slate-600 -z-10 translate-y-px"></div>
            </div>
        `;
    }
    
    if (!isFixed) {
        badge.onclick = (e) => toggleTransportDropdown(e, index);
    }
    
    badge.title = ""; 
    badge.innerHTML = html;
    container.appendChild(badge);
    
    badge.style.top = `${pos.y}px`;
    badge.style.left = `${pos.x}px`;
}

// --- 截图导入航班/车票 ---
let ticketImportImageBase64 = null;
let ticketImportPasteHandler = null;

function showTicketImportModal() {
    ticketImportImageBase64 = null;
    document.getElementById('modal-ticket-import').classList.remove('hidden');
    document.getElementById('ticket-import-placeholder').classList.remove('hidden');
    document.getElementById('ticket-import-preview').classList.add('hidden');
    document.getElementById('ticket-import-preview').src = '';
    document.getElementById('ticket-import-submit').disabled = true;
    document.getElementById('ticket-import-submit').classList.add('opacity-50', 'cursor-not-allowed');
    document.getElementById('ticket-import-status').classList.add('hidden');
    document.getElementById('ticket-import-error').classList.add('hidden');
    document.getElementById('ticket-import-file').value = '';

    document.getElementById('ticket-import-drop').onclick = () => document.getElementById('ticket-import-file').click();
    document.getElementById('ticket-import-file').onchange = (e) => {
        const f = e.target.files[0];
        if (f && f.type.startsWith('image/')) setTicketImageFromFile(f);
    };

    ticketImportPasteHandler = (e) => {
        if (!document.getElementById('modal-ticket-import').classList.contains('hidden') && e.clipboardData?.files?.length) {
            const f = Array.from(e.clipboardData.files).find(f => f.type.startsWith('image/'));
            if (f) { e.preventDefault(); setTicketImageFromFile(f); }
        }
    };
    window.addEventListener('paste', ticketImportPasteHandler);
}

function closeTicketImportModal() {
    document.getElementById('modal-ticket-import').classList.add('hidden');
    if (ticketImportPasteHandler) window.removeEventListener('paste', ticketImportPasteHandler);
    ticketImportPasteHandler = null;
    ticketImportImageBase64 = null;
}

function setTicketImageFromFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
        ticketImportImageBase64 = reader.result;
        document.getElementById('ticket-import-placeholder').classList.add('hidden');
        document.getElementById('ticket-import-preview').classList.remove('hidden');
        document.getElementById('ticket-import-preview').src = ticketImportImageBase64;
        document.getElementById('ticket-import-submit').disabled = false;
        document.getElementById('ticket-import-submit').classList.remove('opacity-50', 'cursor-not-allowed');
    };
    reader.readAsDataURL(file);
}

async function submitTicketImport() {
    if (!ticketImportImageBase64 || !activePlan) return;
    const statusEl = document.getElementById('ticket-import-status');
    const errorEl = document.getElementById('ticket-import-error');
    const btn = document.getElementById('ticket-import-submit');
    statusEl.classList.remove('hidden');
    errorEl.classList.add('hidden');
    statusEl.textContent = '正在识别票据…';
    btn.disabled = true;

    try {
        const res = await fetch('/travel/parse-ticket', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: ticketImportImageBase64 })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '请求失败');

        if (data.type === 'unknown' || data.error) {
            errorEl.textContent = data.error || '无法识别为机票或火车票';
            errorEl.classList.remove('hidden');
            statusEl.classList.add('hidden');
            btn.disabled = false;
            return;
        }

        const dayIdx = getCurrentDayIndex();
        const origin = {
            name: data.origin_name || '出发地',
            address: data.origin_name || null,
            city: data.origin_name || null,
            lat: null,
            lng: null,
            departure_time: data.departure_time || null,
            arrival_time: null
        };
        const destination = {
            name: data.destination_name || '目的地',
            address: data.destination_name || null,
            city: data.destination_name || null,
            lat: null,
            lng: null,
            departure_time: null,
            arrival_time: data.arrival_time || null
        };
        const details = {};
        if (data.flight_no) details.flight_no = data.flight_no;
        if (data.train_no) details.train_no = data.train_no;
        if (data.seat_info) details.seat_info = data.seat_info;
        if (data.departure_time) details.departure_time = data.departure_time;
        if (data.arrival_time) details.arrival_time = data.arrival_time;

        const segment = {
            type: data.type === 'train' ? 'train' : 'flight',
            origin,
            destination,
            distance_km: null,
            duration_minutes: null,
            details
        };
        activePlan.days[dayIdx].segments.push(segment);

        statusEl.textContent = '已加入当天行程';
        closeTicketImportModal();
        renderPlanDetail();
    } catch (e) {
        console.error(e);
        errorEl.textContent = e.message || '识别失败，请重试';
        errorEl.classList.remove('hidden');
        statusEl.classList.add('hidden');
    }
    btn.disabled = false;
}

// --- Interaction Logic ---

function showAddLocationModal(insertAt) {
    insertAtIndex = typeof insertAt === 'number' ? insertAt : null;
    document.getElementById('modal-add-location').classList.remove('hidden');
    document.getElementById('location-search-input').value = '';
    document.getElementById('location-search-input').focus();
    document.getElementById('location-search-results').innerHTML = `
        <div class="text-center text-slate-400 py-10">
            <i class="fas fa-keyboard text-3xl mb-2 opacity-50"></i>
            <p class="text-sm">输入关键词开始搜索</p>
            ${insertAtIndex !== null ? '<p class="text-xs mt-1 text-cyan-600">将添加为当前站点的下一站</p>' : ''}
        </div>
    `;
}

function closeAddLocationModal() {
    document.getElementById('modal-add-location').classList.add('hidden');
}

function handleLocationSearch(keyword) {
    if (debounceTimer) clearTimeout(debounceTimer);
    if (!keyword.trim()) return;

    debounceTimer = setTimeout(async () => {
        const container = document.getElementById('location-search-results');
        container.innerHTML = '<div class="text-center py-4 text-slate-400"><i class="fas fa-spinner fa-spin"></i> 搜索中...</div>';
        
        try {
            const city = activePlan.days[getCurrentDayIndex()].city || ''; 
            const response = await fetch(`/travel/locations/tips?keywords=${encodeURIComponent(keyword)}&city=${encodeURIComponent(city)}`);
            const data = await response.json();
            
            if (data.length === 0) {
                container.innerHTML = '<div class="text-center py-4 text-slate-400">未找到相关地点</div>';
                return;
            }

            container.innerHTML = data.map(item => `
                <div onclick='selectLocation(${JSON.stringify(item)})' class="p-3 hover:bg-slate-50 rounded-lg cursor-pointer transition flex items-center gap-3 border-b border-slate-50 last:border-0">
                    <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 flex-shrink-0">
                        <i class="fas fa-map-pin"></i>
                    </div>
                    <div>
                        <div class="font-medium text-slate-800">${item.name}</div>
                        <div class="text-xs text-slate-400 truncate w-64">${item.district || ''} ${item.address || ''}</div>
                    </div>
                </div>
            `).join('');

        } catch (e) {
            console.error(e);
            container.innerHTML = '<div class="text-center py-4 text-red-400">搜索出错</div>';
        }
    }, 500);
}

async function selectLocation(locationData) {
    closeAddLocationModal();

    // Normalize location object
    const newLoc = {
        name: locationData.name,
        address: locationData.address,
        city: locationData.city || activePlan.days[getCurrentDayIndex()].city || '',
        lat: locationData.location ? parseFloat(locationData.location.split(',')[1]) : null,
        lng: locationData.location ? parseFloat(locationData.location.split(',')[0]) : null
    };

    // 在指定位置插入（由卡片上的 + 触发）；当天尚无行程段时按追加处理
    const daySegments = activePlan.days[getCurrentDayIndex()].segments;
    if (insertAtIndex !== null && daySegments.length > 0) {
        const at = insertAtIndex;
        insertAtIndex = null;
        await insertSegmentAt(at, newLoc);
        renderPlanDetail();
        return;
    }
    if (insertAtIndex !== null) insertAtIndex = null;

    // Case 1: Empty Plan, no temp start
    if (activePlan.days[getCurrentDayIndex()].segments.length === 0 && !activePlan.tempStartLocation) {
        activePlan.tempStartLocation = newLoc;
        if (newLoc.city) activePlan.days[getCurrentDayIndex()].city = newLoc.city;
        renderPlanDetail();
        return;
    }

    // Case 2: Have temp start, creating first segment
    if (activePlan.tempStartLocation) {
        await addSegment(activePlan.tempStartLocation, newLoc);
        activePlan.tempStartLocation = null; // Clear temp
        renderPlanDetail();
        return;
    }

    // Case 3: Have segments, append to last destination
    const lastSeg = activePlan.days[getCurrentDayIndex()].segments[activePlan.days[getCurrentDayIndex()].segments.length - 1];
    await addSegment(lastSeg.destination, newLoc);
    renderPlanDetail();
}

/** 在指定地点索引前插入新地点，并重算前后段路线 */
async function insertSegmentAt(locationIndex, newLoc) {
    const dayIdx = getCurrentDayIndex();
    const segments = activePlan.days[dayIdx].segments;
    const defaultMode = 'driving';

    if (newLoc.city && !activePlan.days[dayIdx].city) {
        activePlan.days[dayIdx].city = newLoc.city;
    }

    document.getElementById('plan-timeline').style.opacity = '0.7';
    try {
        if (locationIndex === 0) {
            const firstOrigin = segments[0].origin;
            const result = await calculateSegmentData(newLoc, firstOrigin, defaultMode);
            segments.unshift({
                type: defaultMode,
                origin: newLoc,
                destination: firstOrigin,
                distance_km: result.distance_km,
                duration_minutes: result.duration_minutes
            });
        } else {
            const prev = segments[locationIndex - 1];
            const [res1, res2] = await Promise.all([
                calculateSegmentData(prev.origin, newLoc, defaultMode),
                calculateSegmentData(newLoc, prev.destination, defaultMode)
            ]).catch(() => [{ distance_km: 0, duration_minutes: 0 }, { distance_km: 0, duration_minutes: 0 }]);
            const seg1 = { type: defaultMode, origin: prev.origin, destination: newLoc, distance_km: res1.distance_km, duration_minutes: res1.duration_minutes };
            const seg2 = { type: defaultMode, origin: newLoc, destination: prev.destination, distance_km: res2.distance_km, duration_minutes: res2.duration_minutes };
            segments.splice(locationIndex - 1, 1, seg1, seg2);
        }
    } catch (e) {
        if (locationIndex === 0) {
            segments.unshift({ type: defaultMode, origin: newLoc, destination: segments[0].origin, distance_km: 0, duration_minutes: 0 });
        } else {
            const prev = segments[locationIndex - 1];
            segments.splice(locationIndex - 1, 1,
                { type: defaultMode, origin: prev.origin, destination: newLoc, distance_km: 0, duration_minutes: 0 },
                { type: defaultMode, origin: newLoc, destination: prev.destination, distance_km: 0, duration_minutes: 0 }
            );
        }
    } finally {
        document.getElementById('plan-timeline').style.opacity = '1';
    }
    ensureDayStayArray(activePlan.days[dayIdx]);
    const stay = activePlan.days[dayIdx].location_stay_minutes;
    if (stay && locationIndex >= 0 && locationIndex <= stay.length) {
        stay.splice(locationIndex, 0, 0);
    }
}

async function addSegment(origin, dest) {
    // Show loading indicator in timeline? For now just await
    const defaultMode = 'driving';
    
    // Calculate details
    try {
        const result = await calculateSegmentData(origin, dest, defaultMode);
        
        const newSegment = {
            type: defaultMode,
            origin: origin,
            destination: dest,
            distance_km: result.distance_km,
            duration_minutes: result.duration_minutes
        };
        
        activePlan.days[getCurrentDayIndex()].segments.push(newSegment);
    } catch (e) {
        alert('无法计算路线: ' + e.message);
        activePlan.days[getCurrentDayIndex()].segments.push({
            type: defaultMode,
            origin: origin,
            destination: dest,
            distance_km: 0,
            duration_minutes: 0
        });
    }
    ensureDayStayArray(activePlan.days[getCurrentDayIndex()]);
}

async function calculateSegmentData(origin, dest, mode) {
    const response = await fetch('/travel/calculate-segment', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            origin: origin.name,
            destination: dest.name,
            mode: mode,
            city: activePlan.days[getCurrentDayIndex()].city
        })
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    return data;
}

// --- 交通方式详情（查看时长/距离/航班车次等）---
function openTransportDetailModal(index) {
    const segment = activePlan?.days?.[getCurrentDayIndex()]?.segments?.[index];
    if (!segment) return;
    viewingDetailSegmentIndex = index;

    const duration = segment.duration_minutes ? formatDuration(segment.duration_minutes * 60) : '--';
    const distance = segment.distance_km ? `${segment.distance_km} km` : '--';
    const dep = segment.details?.departure_time || segment.origin?.departure_time;
    const arr = segment.details?.arrival_time || segment.destination?.arrival_time;
    const isFlightOrTrain = segment.type === 'flight' || segment.type === 'train';

    let typeLabel = '驾车';
    let icon = 'fa-car';
    if (segment.type === 'transit') {
        typeLabel = (segment.details && segment.details.display_label === '城际交通') ? '城际交通' : '公交/地铁';
        icon = 'fa-bus';
    }
    if (segment.type === 'walking') { typeLabel = '步行'; icon = 'fa-walking'; }
    if (segment.type === 'cycling') { typeLabel = '骑行'; icon = 'fa-bicycle'; }
    if (segment.type === 'flight') { typeLabel = segment.details?.flight_no || '航班'; icon = 'fa-plane'; }
    if (segment.type === 'train') { typeLabel = segment.details?.train_no || '高铁/火车'; icon = 'fa-train'; }

    const originName = segment.origin?.name || '起点';
    const destName = segment.destination?.name || '终点';

    let rows = [
        `<div class="flex items-center gap-2 text-slate-800 font-medium"><i class="fas ${icon} text-cyan-600"></i> ${typeLabel}</div>`,
        `<div class="flex justify-between"><span class="text-slate-400">起点</span><span>${originName}</span></div>`,
        `<div class="flex justify-between"><span class="text-slate-400">终点</span><span>${destName}</span></div>`
    ];
    if (isFlightOrTrain) {
        if (dep || arr) rows.push(`<div class="flex justify-between"><span class="text-slate-400">时间</span><span>${dep || '--'} → ${arr || '--'}</span></div>`);
        if (segment.details?.seat_info) rows.push(`<div class="flex justify-between"><span class="text-slate-400">座位</span><span>${segment.details.seat_info}</span></div>`);
        // Always show duration and distance for flight/train segments (even when no dep/arr times)
        rows.push(`<div class="flex justify-between"><span class="text-slate-400">时长</span><span>${duration}</span></div>`);
        rows.push(`<div class="flex justify-between"><span class="text-slate-400">距离</span><span>${distance}</span></div>`);
    } else {
        rows.push(`<div class="flex justify-between"><span class="text-slate-400">时长</span><span>${duration}</span></div>`);
        rows.push(`<div class="flex justify-between"><span class="text-slate-400">距离</span><span>${distance}</span></div>`);
    }

    document.getElementById('transport-detail-content').innerHTML = rows.map(r => `<div class="py-1.5 border-b border-slate-100 last:border-0">${r}</div>`).join('');
    const changeBtn = document.getElementById('transport-detail-change-btn');
    // 票据导入的航班/火车（有 flight_no/train_no）不可更改，用户手动选的高铁可更改
    const isImportedFixed = (segment.type === 'flight' && segment.details?.flight_no) || (segment.type === 'train' && segment.details?.train_no);
    if (isImportedFixed) {
        changeBtn.classList.add('hidden');
    } else {
        changeBtn.classList.remove('hidden');
    }
    document.getElementById('modal-transport-detail').classList.remove('hidden');
}

function closeTransportDetailModal() {
    document.getElementById('modal-transport-detail').classList.add('hidden');
    viewingDetailSegmentIndex = -1;
}

function openTransportModalFromDetail() {
    const idx = viewingDetailSegmentIndex;
    closeTransportDetailModal();
    if (idx < 0) return;
    openTransportModal(idx);
}

// Transport Editing（选择交通方式 - 下拉菜单）
function toggleTransportDropdown(event, index) {
    if (event) event.stopPropagation();

    const segment = activePlan?.days?.[getCurrentDayIndex()]?.segments?.[index];
    // 仅票据导入的航班/火车（带车次或航班号）不可修改
    if (segment && (segment.details?.flight_no || segment.details?.train_no)) {
        return;
    }

    const dropdown = document.getElementById('transport-dropdown');
    
    // 如果点击的是同一个 index 且菜单已显示，则关闭
    if (editingSegmentIndex === index && !dropdown.classList.contains('hidden')) {
        closeTransportDropdown();
        return;
    }

    editingSegmentIndex = index;
    
    // 定位 Dropdown
    const triggerBtn = event.currentTarget;
    const rect = triggerBtn.getBoundingClientRect();
    const dropdownHeight = 220; // Estimated height
    
    // 默认显示在下方
    let top = rect.bottom + 8;
    let left = rect.left;
    
    // 如果底部空间不足，显示在上方
    if (top + dropdownHeight > window.innerHeight) {
        top = rect.top - dropdownHeight - 8;
        dropdown.classList.remove('origin-top');
        dropdown.classList.add('origin-bottom');
    } else {
        dropdown.classList.add('origin-top');
        dropdown.classList.remove('origin-bottom');
    }
    
    // 边界检查 (右侧)
    if (left + 160 > window.innerWidth) {
        left = window.innerWidth - 170;
    }

    dropdown.style.top = `${top}px`;
    dropdown.style.left = `${left}px`;
    
    // 显示
    dropdown.classList.remove('hidden');
    // Force reflow
    void dropdown.offsetWidth;
    dropdown.classList.remove('scale-95', 'opacity-0');

    // 添加一次性全局点击监听以关闭菜单
    requestAnimationFrame(() => {
        document.addEventListener('click', closeTransportDropdownOnOutsideClick);
    });
}

function closeTransportDropdown() {
    const dropdown = document.getElementById('transport-dropdown');
    dropdown.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        dropdown.classList.add('hidden');
    }, 200);

    document.removeEventListener('click', closeTransportDropdownOnOutsideClick);
    // 重置 index，除非是在 selectTransportMode 中调用（那里会用到）
    // 但如果在 selectTransportMode 中调用，会立即重新渲染，所以这里不重置也没关系
    // 为了安全起见，仅在非交互时重置
    // editingSegmentIndex = -1; 
}

function closeTransportDropdownOnOutsideClick(e) {
    const dropdown = document.getElementById('transport-dropdown');
    if (!dropdown.contains(e.target)) {
        closeTransportDropdown();
    }
}

// 保持兼容旧代码调用的空函数或重定向
function openTransportModal(index) {
    // 这里的逻辑已经通过 toggleTransportDropdown 替代
    // 但如果其他地方调用了 openTransportModal，我们需要注意
    // 目前看只有 badge.onclick 调用
    console.warn('Deprecated: openTransportModal called.');
}

function closeTransportModal() {
     closeTransportDropdown();
}

async function selectTransportMode(mode) {
    closeTransportDropdown();
    if (editingSegmentIndex === -1) return;
    
    const segment = activePlan.days[getCurrentDayIndex()].segments[editingSegmentIndex];
    if (segment.type === mode) return; // No change

    // Show loading for the specific connector
    document.getElementById('plan-timeline').style.opacity = '0.7';

    try {
        const result = await calculateSegmentData(segment.origin, segment.destination, mode);
        segment.type = mode;
        segment.distance_km = result.distance_km;
        segment.duration_minutes = result.duration_minutes;
        renderPlanDetail();
    } catch (e) {
        showToast('该交通方式不可用: ' + e.message, 'error');
    } finally {
        document.getElementById('plan-timeline').style.opacity = '1';
    }
}

function removeLocation(index, isLast) {
    if (!confirm('确定移除该地点吗？')) return;
    
    if (activePlan.tempStartLocation) {
        activePlan.tempStartLocation = null;
        renderPlanDetail();
        return;
    }
    
    const segments = activePlan.days[getCurrentDayIndex()].segments;
    
    // Show loading
    document.getElementById('plan-timeline').style.opacity = '0.5';

    // Helper to handle async removal
    const handleRemoval = async () => {
        try {
            const day = activePlan.days[getCurrentDayIndex()];
            ensureDayStayArray(day);
            const stay = day.location_stay_minutes;
            if (index === 0) {
                // Removing start
                if (segments.length === 1) {
                    activePlan.tempStartLocation = segments[0].destination;
                    segments.shift();
                    if (stay.length > 0) stay.shift();
                } else {
                    segments.shift();
                    if (stay.length > 0) stay.shift();
                }
            } else if (isLast) {
                segments.pop();
                if (stay.length > 0) stay.pop();
            } else {
                 // Removing middle node: Merge segments
                 const prevSeg = segments[index-1];
                 const nextSeg = segments[index];
                 const newDest = nextSeg.destination;
                 const newOrigin = prevSeg.origin;
                 
                 segments.splice(index-1, 2);
                 if (stay.length > index) stay.splice(index, 1);
                 
                 const res = await calculateSegmentData(newOrigin, newDest, 'driving');
                 segments.splice(index-1, 0, {
                     type: 'driving',
                     origin: newOrigin,
                     destination: newDest,
                     distance_km: res.distance_km,
                     duration_minutes: res.duration_minutes
                 });
            }
            renderPlanDetail();
        } catch(e) {
             console.error(e);
             showToast('操作失败，请重试', 'error');
             renderPlanDetail(); // Re-render to restore state visual
        } finally {
             document.getElementById('plan-timeline').style.opacity = '1';
        }
    };
    
    handleRemoval();
}

// 保存布局按钮逻辑
async function saveLayout() {
    if (!activePlan) return;
    
    const btn = document.querySelector('button[onclick="saveLayout()"]');
    const originalHtml = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin text-cyan-500"></i> 保存中';
    btn.disabled = true;

    // 确保所有当前的 style.left/top 都已同步到 activePlan.days[dayIndex].layout
    // 虽然 handleFreeMouseUp 已经做了，但为了保险起见，再次遍历当前 DOM 状态
    // (仅针对当前显示的 tab)
    const dayIndex = typeof activeDetailTab === 'number' ? activeDetailTab : 0;
    const container = document.getElementById(`snake-container-${dayIndex}`);
    
    if (container) {
        const day = activePlan.days[dayIndex];
        if (!day.layout) day.layout = [];
        
        container.querySelectorAll('.snake-item').forEach(el => {
            const idParts = el.id.split('-'); // snake-item-0-1
            if (idParts.length >= 4) {
                const nodeIdx = parseInt(idParts[3]);
                const left = parseFloat(el.style.left);
                const top = parseFloat(el.style.top);
                
                if (!isNaN(nodeIdx) && !isNaN(left) && !isNaN(top)) {
                    day.layout[nodeIdx] = { x: left, y: top };
                }
            }
        });
        
        // 还要更新容器高度
        // (Wait, height is style, not saved in plan json usually, unless we add a prop)
        // Currently layout coordinates are saved, height is derived on render.
    }

    try {
        // 调用通用保存逻辑
        // 我们手动调用 fetch 以便自定义 Toast
        const planToSave = JSON.parse(JSON.stringify(activePlan));
        delete planToSave.tempStartLocation;
        (planToSave.days || []).forEach(d => {
            (d.segments || []).forEach(seg => { delete seg._amapAttempted; });
        });

        const response = await fetch('/travel/plans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(planToSave)
        });
        
        if (response.ok) {
            showToast('画布布局已保存');
            const saved = await response.json();
            if (saved.id) activePlan.id = saved.id;
            if (saved.created_at) activePlan.created_at = saved.created_at;
        } else {
            showToast('布局保存失败', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('保存出错，请检查网络', 'error');
    } finally {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}

async function saveActivePlan() {
    if (!activePlan) return;
    
    // Remove temp props
    const planToSave = JSON.parse(JSON.stringify(activePlan));
    delete planToSave.tempStartLocation;
    
    const saveBtn = document.querySelector('button[onclick="saveActivePlan()"]');
    const originalContent = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中';
    saveBtn.disabled = true;

    try {
        const response = await fetch('/travel/plans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(planToSave)
        });
        
        if (response.ok) {
            showToast('行程已保存');
            activePlan = await response.json(); // Update ID/timestamp
        } else {
            showToast('保存失败', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('保存出错，请检查网络', 'error');
    } finally {
        saveBtn.innerHTML = originalContent;
        saveBtn.disabled = false;
    }
}

/** 静默保存行程（不弹 toast、不更新按钮状态），用于后台自动补全数据后持久化 */
async function saveActivePlanSilently() {
    if (!activePlan) return;
    const planToSave = JSON.parse(JSON.stringify(activePlan));
    delete planToSave.tempStartLocation;
    // 清理内部标记字段
    (planToSave.days || []).forEach(d => {
        (d.segments || []).forEach(seg => { delete seg._amapAttempted; });
    });
    try {
        const response = await fetch('/travel/plans', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(planToSave)
        });
        if (response.ok) {
            const saved = await response.json();
            // 仅更新 id/timestamp，不覆盖内存中的标记
            if (saved.id) activePlan.id = saved.id;
            if (saved.created_at) activePlan.created_at = saved.created_at;
        }
    } catch (e) {
        console.error('[auto-save]', e);
    }
}

// --- Title Inline Edit ---
function startEditTitle() {
    const titleEl = document.getElementById('detail-title');
    const inputEl = document.getElementById('detail-title-input');
    const titleGroup = titleEl.closest('.group\\/title');

    inputEl.value = activePlan.title || '';
    titleGroup.classList.add('hidden');
    inputEl.classList.remove('hidden');
    inputEl.focus();
    inputEl.select();
}

function finishEditTitle() {
    const titleEl = document.getElementById('detail-title');
    const inputEl = document.getElementById('detail-title-input');
    const titleGroup = titleEl.closest('.group\\/title');

    const newTitle = inputEl.value.trim();
    if (newTitle && activePlan) {
        activePlan.title = newTitle;
        titleEl.textContent = newTitle;
    }
    inputEl.classList.add('hidden');
    titleGroup.classList.remove('hidden');
}

// Toast Notification Helper
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed top-24 right-4 z-[70] px-6 py-3 rounded-lg shadow-xl text-white font-medium transform transition-all duration-300 translate-x-full ${type === 'error' ? 'bg-red-500' : 'bg-green-500'}`;
    toast.innerHTML = `<i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'} mr-2"></i> ${message}`;
    document.body.appendChild(toast);
    
    // Slide in
    setTimeout(() => toast.classList.remove('translate-x-full'), 10);
    
    // Slide out
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Ensure theme icons are updated after DOM is ready
    updateThemeIcons(getTheme());
    // Set default view to home card navigation
    showView('home');
});
