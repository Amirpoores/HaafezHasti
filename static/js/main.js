// ===== JavaScript ساده شده =====

let currentGhazal = null;

// تغییر تب
function switchTab(tabName) {
    // مخفی کردن همه تب‌ها
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // مخفی کردن نتایج
    document.querySelectorAll('.result').forEach(result => {
        result.classList.remove('show');
    });
    
    // غیرفعال کردن همه دکمه‌ها
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // فعال کردن تب و دکمه انتخاب شده
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// نمایش نتیجه
function showResult(contentHtml) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = contentHtml;
    document.getElementById('result').classList.add('show');
}

// نمایش loading
function showLoading() {
    document.getElementById('result').classList.add('show');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';
}

// فال تصادفی
function getFal() {
    showLoading();
    
    fetch('/get_fal')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            currentGhazal = data;
            
            const contentHtml = `
                <div class="ghazal-display">
                    <div class="ghazal-header">
                        <div class="ghazal-number">غزل شماره ${data.number}</div>
                        <div class="ghazal-title">${data.title}</div>
                    </div>
                    <div class="ghazal-text">${data.text}</div>
                </div>
                
                <div class="fal-interpretation">
                    <div class="interpretation-title">تفسیر فال شما</div>
                    <div class="interpretation-text">${data.interpretation}</div>
                </div>
                
                <div class="button-group">
                    <button class="fal-button" onclick="getFal()">🔄 فال جدید</button>
                </div>
            `;
            
            showResult(contentHtml);
        })
        .catch(error => {
            showError('خطا در دریافت فال: ' + error.message);
        });
}

// غزل با شماره
function getSpecificGhazal() {
    const number = document.getElementById('ghazal-number').value;
    
    if (!number || number < 1 || number > 495) {
        showError('لطفاً شماره غزل را بین 1 تا 495 وارد کنید');
        return;
    }
    
    showLoading();
    
    fetch(`/get_ghazal/${number}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            currentGhazal = data;
            
            const contentHtml = `
                <div class="ghazal-display">
                    <div class="ghazal-header">
                        <div class="ghazal-number">غزل شماره ${data.number}</div>
                        <div class="ghazal-title">${data.title}</div>
                    </div>
                    <div class="ghazal-text">${data.text}</div>
                </div>
                
                <div class="button-group">
                    <button class="fal-button button-secondary" onclick="getRandomGhazal()">🎲 غزل تصادفی</button>
                </div>
            `;
            
            showResult(contentHtml);
        })
        .catch(error => {
            showError('خطا در دریافت غزل: ' + error.message);
        });
}

// غزل تصادفی
function getRandomGhazal() {
    const randomNumber = Math.floor(Math.random() * 495) + 1;
    document.getElementById('ghazal-number').value = randomNumber;
    getSpecificGhazal();
}

// جستجو
function searchGhazals() {
    const query = document.getElementById('search-input').value.trim();
    
    if (!query) {
        showError('لطفاً متن جستجو را وارد کنید');
        return;
    }
    
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            let searchHtml = `<p style="text-align: center; margin-bottom: 20px; color: var(--coffee-brown);">نتایج جستجو برای: "<strong>${data.query}</strong>" (${data.count} نتیجه)</p>`;
            
            if (data.results.length === 0) {
                searchHtml += '<p style="text-align: center; color: var(--text-brown);">هیچ نتیجه‌ای یافت نشد.</p>';
            } else {
                data.results.forEach(item => {
                    searchHtml += `
                        <div class="search-item" onclick="loadGhazalFromSearch(${item.number})">
                            <div class="search-item-number">غزل ${item.number}</div>
                            <div class="search-item-title">${item.title}</div>
                            <div class="search-item-preview">${item.preview}</div>
                        </div>
                    `;
                });
            }
            
            document.getElementById('search-content').innerHTML = searchHtml;
            document.getElementById('search-results').classList.add('show');
        })
        .catch(error => {
            showError('خطا در جستجو: ' + error.message);
        });
}

// بارگذاری غزل از نتایج جستجو
function loadGhazalFromSearch(number) {
    document.getElementById('ghazal-number').value = number;
    switchTab('ghazal');
    getSpecificGhazal();
}

// پاک کردن جستجو
function clearSearch() {
    document.getElementById('search-input').value = '';
    document.getElementById('search-results').classList.remove('show');
}

// نمایش خطا
function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'block';
    document.getElementById('content').innerHTML = `
        <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 15px; margin: 20px 0; border: 2px solid #f5c6cb; text-align: center;">
            ${message}
        </div>
    `;
    document.getElementById('result').classList.add('show');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners برای input ها
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchGhazals();
            }
        });
    }

    const ghazalNumberInput = document.getElementById('ghazal-number');
    if (ghazalNumberInput) {
        ghazalNumberInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                getSpecificGhazal();
            }
        });
    }
});