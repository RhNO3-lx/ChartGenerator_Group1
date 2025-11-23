


// 开始标题生成
async function startTitleGeneration() {
    if (!selectedVariation) {
        alert('请先选择一个图表类型');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectTitleBtn').disabled = true;
    document.getElementById('regenerateTitleBtn').disabled = true;

    try {
        // 开始标题生成
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

// 重新生成标题
async function regenerateTitle() {
    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectTitleBtn').disabled = true;
    document.getElementById('regenerateTitleBtn').disabled = true;

    try {
        // 调用重新生成API
        const response = await fetch(`/api/regenerate_title/${currentDataFile}`);
        const result = await response.json();

        if (result.status === 'started') {
            // 轮询状态直到完成
            checkStatus();
        }

    } catch (error) {
        console.error('重新生成标题失败:', error);
        alert('重新生成标题失败，请重试');
        hideLoading();
    }
}

// 显示标题选择（3选1版本）
async function showTitleSelection() {
    try {
        const response = await fetch(`/api/status`);
        const status = await response.json();

        const titleOptions = status.title_options || {};
        const titleKeys = Object.keys(titleOptions);

        if (titleKeys.length > 0) {
            const container = document.getElementById('titleContainer');
            container.innerHTML = '';

            // 创建3个标题选项
            for (let i = 0; i < 3; i++) {
                const titleKey = `title_${i}.png`;
                const titleData = titleOptions[titleKey];

                if (titleData && titleData.success) {
                    const item = document.createElement('div');
                    item.className = 'title-item';
                    item.setAttribute('data-filename', titleKey);

                    item.innerHTML = `
                        <div class="title-image-container">
                            <img class="title-image" src="/currentfilepath/${titleKey}?t=${Date.now()}" alt="标题 ${i+1}">
                        </div>
                        <div class="title-text">"${titleData.title_text}"</div>
                    `;

                    container.appendChild(item);
                }
            }

            // 设置点击事件
            setupTitleSelection();
        }

        // 启用按钮
        document.getElementById('selectTitleBtn').disabled = false;
        document.getElementById('regenerateTitleBtn').disabled = false;

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

// 设置标题选择事件
function setupTitleSelection() {
    const titleItems = document.querySelectorAll('.title-item');
    const selectBtn = document.getElementById('selectTitleBtn');

    titleItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            titleItems.forEach(t => t.classList.remove('selected'));

            // 检查选择是否改变
            if (selectedTitle != this.getAttribute('data-filename') && selectedTitle) {
                hideCards(["pictogramCard", "resultCard"]);
            }

            // 添加选中状态
            this.classList.add('selected');
            selectedTitle = this.getAttribute('data-filename');

            selectBtn.disabled = false;
        });
    });
}

// 获取并显示标题文字
async function fetchAndDisplayTitleText() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        const titleTextDisplay = document.getElementById('titleTextDisplay');
        if (status.current_title_text) {
            titleTextDisplay.textContent = `"${status.current_title_text}"`;
        } else if (status.title_options && Object.keys(status.title_options).length > 0) {
            const firstTitle = Object.values(status.title_options)[0];
            if (firstTitle && firstTitle.title_text) {
                titleTextDisplay.textContent = `"${firstTitle.title_text}"`;
            }
        }
    } catch (error) {
        console.error('获取标题文字失败:', error);
    }
}
