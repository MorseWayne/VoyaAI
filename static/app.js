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

let currentPlanData = null;

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
            <p class="text-xl text-gray-600">正在为您规划最佳路线...</p>
            <p class="text-sm text-gray-400 mt-2">正在计算距离和时间</p>
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
        resultsDiv.innerHTML = '<p class="text-center text-gray-500">未找到合适的路线</p>';
        return;
    }

    const totalDuration = parseFloat(data.total_duration_hours) * 60; // hours to minutes
    const totalDist = data.total_distance_km;

    let html = `
        <div class="w-full bg-white p-6 rounded-xl shadow-sm">
            <h3 class="text-xl font-bold text-dark mb-4 flex justify-between items-center">
                <span>规划结果</span>
                <div class="flex items-center gap-2">
                    <span class="text-sm font-normal text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                        总程: ${totalDist}km / 约 ${Math.round(totalDuration)}分钟
                    </span>
                    <button onclick="saveCurrentPlan()" class="text-sm bg-primary text-white px-3 py-2 rounded-lg hover:bg-dark transition flex items-center shadow-sm">
                        <i class="fas fa-plus mr-1"></i> 保存行程
                    </button>
                </div>
            </h3>
            <div class="relative border-l-4 border-primary ml-4 pl-8 space-y-8">
    `;

    data.poi_details.forEach((loc, index) => {
        const isLast = index === data.poi_details.length - 1;
        const segment = !isLast ? data.segments[index] : null;

        html += `
            <div class="relative">
                <div class="absolute -left-[42px] bg-primary text-white w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-md border-2 border-white">
                    ${index + 1}
                </div>
                <div class="bg-gray-50 p-4 rounded-lg hover:bg-yellow-50 transition border border-gray-100">
                    <h4 class="font-bold text-lg text-gray-800">${loc.name}</h4>
                    <p class="text-sm text-gray-500 mt-1"><i class="fas fa-map-marker-alt mr-1"></i> ${loc.address || '地址未知'}</p>
                </div>
                ${!isLast && segment ? `
                    <div class="mt-4 mb-2 text-sm text-gray-500 pl-2 flex items-center gap-2">
                        <i class="fas fa-arrow-down text-primary"></i>
                        <span>约 ${segment.duration_m}分钟</span>
                        <span class="text-gray-300">|</span>
                        <span>${segment.distance_km}km</span>
                        <span class="text-gray-300">|</span>
                        <span class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">${segment.mode}</span>
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
                 
                 // Map mode strictly to enum
                 let mode = 'driving';
                 if (seg.mode.includes('公交') || seg.mode.includes('地铁') || seg.mode.includes('Transit')) mode = 'transit';
                 if (seg.mode.includes('步行')) mode = 'walking';
                 if (seg.mode.includes('骑行')) mode = 'cycling';
                 
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
                     duration_minutes: parseFloat(seg.duration_m)
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
                <div class="col-span-full text-center py-12 bg-gray-50 rounded-xl border-dashed border-2 border-gray-200">
                    <i class="fas fa-inbox text-4xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500">暂无保存的行程</p>
                </div>
            `;
            return;
        }

        listDiv.innerHTML = plans.map(plan => `
            <div class="bg-white rounded-xl shadow-md hover:shadow-lg transition p-6 border-t-4 border-primary relative group">
                <button onclick="deletePlan('${plan.id}')" class="absolute top-4 right-4 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition">
                    <i class="fas fa-trash-alt"></i>
                </button>
                <h3 class="font-bold text-xl mb-2 text-dark truncate" title="${plan.title || '未命名行程'}">${plan.title || '未命名行程'}</h3>
                <div class="text-sm text-gray-500 mb-4 space-y-1">
                    <p><i class="far fa-calendar-alt w-5"></i> ${new Date(plan.created_at || Date.now()).toLocaleDateString()}</p>
                    <p><i class="fas fa-map-marker-alt w-5"></i> ${plan.days ? plan.days.length : 0} 天行程</p>
                </div>
                <button onclick="viewPlan('${plan.id}')" class="w-full mt-2 bg-secondary text-dark hover:bg-primary hover:text-white font-medium py-2 rounded-lg transition">
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

async function createNewPlan() {
    // Reset and Show Wizard
    document.getElementById('create-title').value = '';
    document.getElementById('create-date').valueAsDate = new Date();
    document.getElementById('create-dest-list').innerHTML = '';
    
    // Add one default item
    addDestinationItem();
    
    showView('create-plan');
}

let citySearchDebounce = null;

function addDestinationItem() {
    const list = document.getElementById('create-dest-list');
    const id = 'dest-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    
    const div = document.createElement('div');
    div.className = 'flex gap-3 items-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm group animate-fade-in relative z-10'; // Added relative for z-index
    div.innerHTML = `
        <div class="cursor-move text-slate-300 hover:text-slate-500 px-2">
            <i class="fas fa-grip-vertical"></i>
        </div>
        <div class="flex-grow relative">
            <input type="text" 
                   placeholder="输入城市/目的地 (如: 成都)" 
                   class="dest-city w-full outline-none text-slate-700 font-medium placeholder:font-normal placeholder:text-slate-300" 
                   oninput="handleDestinationCitySearch(this, '${id}-results')"
                   onfocus="handleDestinationCitySearch(this, '${id}-results')"
                   onblur="setTimeout(() => document.getElementById('${id}-results').classList.add('hidden'), 200)"
                   autocomplete="off">
            <div id="${id}-results" class="absolute top-full left-0 w-full bg-white shadow-xl rounded-xl border border-slate-100 z-50 hidden max-h-60 overflow-y-auto mt-2">
                <!-- Search Results -->
            </div>
        </div>
        <div class="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
            <input type="number" value="1" min="1" max="30" class="dest-days w-12 bg-transparent outline-none text-center font-bold text-cyan-600" onchange="updateTotalDays()">
            <span class="text-xs text-slate-400">天</span>
        </div>
        <button onclick="this.parentElement.remove(); updateTotalDays()" class="w-8 h-8 flex items-center justify-center text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition">
            <i class="fas fa-trash-alt"></i>
        </button>
    `;
    
    // Fix z-index stacking context for dropdowns
    // Newer items should be on top? No, dropdowns need to float over subsequent items.
    // CSS grid/flex layout usually handles z-index by order. 
    // We might need to manually set z-index descending if they overlap.
    // For now, let's hope absolute positioning works well. 
    // Actually, subsequent relative items will cover the dropdown of previous items if z-index is not handled.
    // Let's set a diminishing z-index based on child count to be safe, or just high z-index on hover/focus.
    // A simple fix is setting style.zIndex on the container when input is focused.
    const input = div.querySelector('input');
    input.addEventListener('focus', () => { div.style.zIndex = 100; });
    input.addEventListener('blur', () => { setTimeout(() => div.style.zIndex = 10, 200); });

    list.appendChild(div);
    updateTotalDays();
}

function handleDestinationCitySearch(input, resultsId) {
    const resultsDiv = document.getElementById(resultsId);
    const keyword = input.value.trim();
    
    if (!keyword) {
        resultsDiv.classList.add('hidden');
        return;
    }
    
    if (citySearchDebounce) clearTimeout(citySearchDebounce);
    
    citySearchDebounce = setTimeout(async () => {
        try {
            resultsDiv.innerHTML = '<div class="p-3 text-center text-slate-400 text-xs"><i class="fas fa-spinner fa-spin"></i> 搜索中...</div>';
            resultsDiv.classList.remove('hidden');
            
            // Call API with city_search=true to filter for administrative regions
            const response = await fetch(`/travel/locations/tips?keywords=${encodeURIComponent(keyword)}&city_search=true`);
            const data = await response.json();
            
            if (!data || data.length === 0) {
                resultsDiv.innerHTML = '<div class="p-3 text-center text-slate-400 text-xs">未找到相关城市</div>';
                return;
            }
            
            resultsDiv.innerHTML = data.map(item => `
                <div class="px-4 py-3 hover:bg-cyan-50 cursor-pointer border-b border-slate-50 last:border-0 transition"
                     onmousedown="selectDestinationCity(this, '${item.name.replace(/'/g, "\\'")}')">
                    <div class="font-medium text-slate-700 text-sm flex justify-between">
                        <span>${item.name}</span>
                        <span class="text-xs text-cyan-600 bg-cyan-50 px-1.5 py-0.5 rounded ml-2 whitespace-nowrap">选择</span>
                    </div>
                    ${item.district ? `<div class="text-xs text-slate-400 mt-0.5 truncate">${item.district}</div>` : ''}
                </div>
            `).join('');
            
        } catch (e) {
            console.error(e);
            resultsDiv.classList.add('hidden');
        }
    }, 300);
}

function selectDestinationCity(element, cityName) {
    const container = element.closest('.flex-grow');
    const input = container.querySelector('input');
    const results = container.querySelector('div[id$="-results"]');
    
    input.value = cityName;
    results.classList.add('hidden');
    updateTotalDays(); // Trigger any updates
}

function updateTotalDays() {
    const daysInputs = document.querySelectorAll('.dest-days');
    let total = 0;
    daysInputs.forEach(input => total += parseInt(input.value) || 0);
    document.getElementById('total-days').textContent = total;
}

async function submitCreatePlan() {
    let title = document.getElementById('create-title').value.trim();
    const startDateStr = document.getElementById('create-date').value;
    
    // Gather destinations
    const destItems = document.querySelectorAll('#create-dest-list > div');
    const legs = [];
    
    destItems.forEach(item => {
        const city = item.querySelector('.dest-city').value.trim();
        const days = parseInt(item.querySelector('.dest-days').value) || 1;
        if (city) {
            legs.push({ city, days });
        }
    });
    
    if (legs.length === 0) {
        showToast('请至少添加一个游玩城市', 'error');
        return;
    }

    // Show loading
    const saveBtn = document.querySelector('button[onclick="submitCreatePlan()"]');
    const originalContent = saveBtn.innerHTML;
    saveBtn.disabled = true;

    // Auto-generate title via LLM if empty
    if (!title) {
        saveBtn.innerHTML = '<i class="fas fa-magic fa-spin"></i> AI 生成标题中...';
        const totalDays = legs.reduce((sum, l) => sum + l.days, 0);
        const cities = legs.map(l => l.city);
        try {
            const res = await fetch('/travel/generate-title', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ cities, days: totalDays })
            });
            const data = await res.json();
            title = data.title || `${cities.join('、')}${totalDays}日游`;
        } catch (e) {
            console.warn('Auto title generation failed:', e);
            title = `${cities.join('、')}${totalDays}日游`;
        }
        // Fill back into the input for user to see
        document.getElementById('create-title').value = title;
    }

    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';

    // Build Days
    const days = [];
    let currentDate = new Date(startDateStr);
    let dayIndex = 1;
    
    legs.forEach(leg => {
        for (let i = 0; i < leg.days; i++) {
            days.push({
                day_index: dayIndex,
                date: currentDate.toISOString().split('T')[0], // YYYY-MM-DD
                city: leg.city,
                segments: []
            });
            
            // Next day
            currentDate.setDate(currentDate.getDate() + 1);
            dayIndex++;
        }
    });

    const newPlan = {
        title: title,
        days: days
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
            
            // Ensure data structure
            if (!activePlan.days) activePlan.days = [];
            
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
let editingSegmentIndex = -1;
let debounceTimer = null;

async function viewPlan(planId) {
    try {
        const response = await fetch(`/travel/plans/${planId}`);
        if (!response.ok) throw new Error('Failed to load plan');
        
        activePlan = await response.json();
        
        // Ensure data structure integrity
        if (!activePlan.days) activePlan.days = [];
        if (activePlan.days.length === 0) activePlan.days.push({ day_index: 1, segments: [] });
        if (!activePlan.days[0].segments) activePlan.days[0].segments = [];
        
        showView('plan-detail');
        renderPlanDetail();
    } catch (error) {
        console.error(error);
        alert('无法加载行程详情');
    }
}

function renderPlanDetail() {
    const titleEl = document.getElementById('detail-title');
    const subtitleEl = document.getElementById('detail-subtitle');
    const timelineEl = document.getElementById('plan-timeline');
    
    titleEl.textContent = activePlan.title || '未命名行程';
    const dayCount = activePlan.days.length;
    const spotCount = activePlan.days.reduce((acc, day) => {
        // Approximate spots: segments + 1
        return acc + (day.segments.length > 0 ? day.segments.length + 1 : 0);
    }, 0);
    subtitleEl.textContent = `${dayCount} 天 · ${spotCount} 个地点`;

    // Render Timeline
    const segments = activePlan.days[0].segments;
    
    if (segments.length === 0) {
        // Check if we have a start location stored (temporary state)
        if (activePlan.tempStartLocation) {
             timelineEl.innerHTML = `
                <div class="relative pl-8">
                    <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-slate-200"></div>
                    ${renderLocationCard(activePlan.tempStartLocation, 0, true)}
                    <div class="mt-8 text-center text-slate-400 text-sm bg-slate-50 p-4 rounded-lg border border-dashed border-slate-300">
                        <i class="fas fa-arrow-down mb-2 block"></i>
                        点击右下角 "+" 添加下一个地点
                    </div>
                </div>
            `;
        } else {
             timelineEl.innerHTML = `
                <div class="text-center py-20 text-slate-400">
                    <div class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-map-signs text-3xl text-slate-300"></i>
                    </div>
                    <p>还没有添加任何地点</p>
                    <p class="text-sm mt-2">点击右下角 "+" 开始规划</p>
                </div>
            `;
        }
        return;
    }

    let html = `<div class="relative pl-8 pb-4">
        <div class="absolute left-[11px] top-4 bottom-4 w-0.5 bg-slate-200"></div>`;
    
    // Render loop
    segments.forEach((seg, index) => {
        // Origin
        html += renderLocationCard(seg.origin, index);
        
        // Transport Connector
        html += renderTransportConnector(seg, index);
        
        // If last segment, render destination
        if (index === segments.length - 1) {
            html += renderLocationCard(seg.destination, index + 1, true);
        }
    });

    html += `</div>`;
    timelineEl.innerHTML = html;
}

function renderLocationCard(location, index, isLast = false) {
    return `
        <div class="relative mb-6 group">
            <div class="absolute -left-[41px] top-0 w-6 h-6 rounded-full border-2 border-white shadow-md z-10 
                 ${isLast ? 'bg-red-500' : 'bg-primary'} text-white flex items-center justify-center text-xs font-bold">
                ${index + 1}
            </div>
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-bold text-slate-800">${location.name}</h4>
                        <p class="text-xs text-slate-500 mt-1 truncate max-w-[200px] md:max-w-md">
                            <i class="fas fa-map-marker-alt mr-1"></i> ${location.address || location.city || '未知地址'}
                        </p>
                    </div>
                    <button class="text-slate-300 hover:text-red-500 transition px-2" onclick="removeLocation(${index}, ${isLast})">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function renderTransportConnector(segment, index) {
    const duration = segment.duration_minutes ? formatDuration(segment.duration_minutes * 60) : '--';
    const distance = segment.distance_km ? `${segment.distance_km}km` : '--';
    
    let icon = 'fa-car';
    let label = '驾车';
    if (segment.type === 'transit') { icon = 'fa-bus'; label = '公交'; }
    if (segment.type === 'walking') { icon = 'fa-walking'; label = '步行'; }
    if (segment.type === 'cycling') { icon = 'fa-bicycle'; label = '骑行'; }

    return `
        <div class="ml-4 mb-6 relative">
            <div onclick="openTransportModal(${index})" 
                 class="inline-flex items-center gap-3 bg-slate-50 hover:bg-cyan-50 border border-slate-200 hover:border-cyan-200 px-3 py-1.5 rounded-lg cursor-pointer transition group">
                <div class="text-slate-400 group-hover:text-cyan-600">
                    <i class="fas ${icon}"></i>
                    <span class="text-xs ml-1">${label}</span>
                </div>
                <div class="w-px h-3 bg-slate-300"></div>
                <div class="text-xs text-slate-500 font-mono">
                    ${duration} · ${distance}
                </div>
                <i class="fas fa-chevron-right text-[10px] text-slate-300 ml-1"></i>
            </div>
        </div>
    `;
}

// --- Interaction Logic ---

function showAddLocationModal() {
    document.getElementById('modal-add-location').classList.remove('hidden');
    document.getElementById('location-search-input').value = '';
    document.getElementById('location-search-input').focus();
    document.getElementById('location-search-results').innerHTML = `
        <div class="text-center text-slate-400 py-10">
            <i class="fas fa-keyboard text-3xl mb-2 opacity-50"></i>
            <p class="text-sm">输入关键词开始搜索</p>
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
            const city = activePlan.days[0].city || ''; 
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
        city: locationData.city || activePlan.days[0].city || '',
        lat: locationData.location ? parseFloat(locationData.location.split(',')[1]) : null,
        lng: locationData.location ? parseFloat(locationData.location.split(',')[0]) : null
    };

    // Case 1: Empty Plan, no temp start
    if (activePlan.days[0].segments.length === 0 && !activePlan.tempStartLocation) {
        activePlan.tempStartLocation = newLoc;
        if (newLoc.city) activePlan.days[0].city = newLoc.city; // Set plan city context
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
    const lastSeg = activePlan.days[0].segments[activePlan.days[0].segments.length - 1];
    await addSegment(lastSeg.destination, newLoc);
    renderPlanDetail();
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
        
        activePlan.days[0].segments.push(newSegment);
    } catch (e) {
        alert('无法计算路线: ' + e.message);
        // Add anyway but with empty data
         activePlan.days[0].segments.push({
            type: defaultMode,
            origin: origin,
            destination: dest,
            distance_km: 0,
            duration_minutes: 0
        });
    }
}

async function calculateSegmentData(origin, dest, mode) {
    const response = await fetch('/travel/calculate-segment', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            origin: origin.name,
            destination: dest.name,
            mode: mode,
            city: activePlan.days[0].city
        })
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    return data;
}

// Transport Editing
function openTransportModal(index) {
    editingSegmentIndex = index;
    document.getElementById('modal-select-transport').classList.remove('hidden');
}

function closeTransportModal() {
    document.getElementById('modal-select-transport').classList.add('hidden');
}

async function selectTransportMode(mode) {
    closeTransportModal();
    if (editingSegmentIndex === -1) return;
    
    const segment = activePlan.days[0].segments[editingSegmentIndex];
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
    
    const segments = activePlan.days[0].segments;
    
    // Show loading
    document.getElementById('plan-timeline').style.opacity = '0.5';

    // Helper to handle async removal
    const handleRemoval = async () => {
        try {
            if (index === 0) {
                // Removing start
                if (segments.length === 1) {
                    activePlan.tempStartLocation = segments[0].destination;
                    segments.shift();
                } else {
                    segments.shift();
                }
            } else if (isLast) {
                segments.pop();
            } else {
                 // Removing middle node: Merge segments
                 const prevSeg = segments[index-1];
                 const nextSeg = segments[index];
                 const newDest = nextSeg.destination;
                 const newOrigin = prevSeg.origin;
                 
                 segments.splice(index-1, 2);
                 
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
    // Set default view to home card navigation
    showView('home');
});
