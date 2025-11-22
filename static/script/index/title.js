


// 开始标题生成
async function startTitleGeneration() {
    if (!selectedVariation) {
        alert('请先选择一个图表类型');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectTitleBtn').disabled = true;

    try {
        // 开始布局抽取
        const response = await fetch(`/api/start_title_generation/${currentDataFile}`);
        const result = await response.json();
        
        if (result.status === 'started') {
            // 轮询状态直到完成
            checkStatus();
        }
        
    } catch (error) {
        console.error('标题生成失败:', error);
        alert('标题生成失败，请重试');
        hideLoading();
    }
}

// 显示标题选择
async function showTitleSelection() {
    try {
        const response = await fetch(`/api/titles`);
        const titles = await response.json();
        
        if (titles) {
            // 主图处理
            const mainTitle = document.getElementById('mainTitle');
            const mainImg = mainTitle.querySelector('.selection-image');
            mainImg.src = `static/img/loading.gif`;
            mainTitle.setAttribute('data-filename', titles[0]);
            mainTitle.setAttribute('data-type', 'origin');
            mainTitle.setAttribute('data-index', '0'); // 主标题索引为0
        
            // 后台替换主图
            loadImageWhenReady(mainImg, `/currentfilepath/title_0.png`);

            // 设置生成的标题选项
            for (let i = 1; i < 5; i++) {
                const titleOption = document.getElementById(`titleOption${i}`);
                const titleImg = titleOption.querySelector('.selection-image');
                titleOption.style.display = 'block'; // 确保显示

                if (titles[i]) {
                    titleImg.src = `static/img/loading.gif`;
                    titleOption.setAttribute('data-filename', titles[i]);
                    titleOption.setAttribute('data-type', 'generated');
                    titleOption.setAttribute('data-index', String(i)); // 选项索引为1,2,3,4（对应Art-Title1.png到Art-Title4.png）

                    // 后台替换选项图
                    loadImageWhenReady(titleImg, `/currentfilepath/title_${i}.png`);
                }
            }
        }
        
        // 设置标题选择事件
        setupTitleSelection();
        
        // 显示标题卡片
        const titleCard = document.getElementById('titleCard');
        titleCard.classList.remove('hidden');
        titleCard.classList.add('fade-in');
        titleCard.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('获取标题失败:', error);
        alert('获取标题失败，请重试');
    }
}

// 设置标题选择
function setupTitleSelection() {
    const titleItems = document.querySelectorAll('#titleCard .selection-item');
    const selectBtn = document.getElementById('selectTitleBtn');
    
    titleItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            titleItems.forEach(title => title.classList.remove('selected'));
            
            // 添加选中状态
            this.classList.add('selected');
            selectedTitle = this.getAttribute('data-filename');
            selectedTitleIndex = parseInt(this.getAttribute('data-index')) || 0;
            selectBtn.disabled = false;
        });
    });
}
