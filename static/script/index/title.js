


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

// 显示标题选择（单张显示版本）
async function showTitleSelection() {
    try {
        const response = await fetch(`/api/titles`);
        const titles = await response.json();

        if (titles && titles.length > 0) {
            // 单张图片显示
            const mainTitle = document.getElementById('mainTitle');
            const mainImg = mainTitle.querySelector('.selection-image');
            mainImg.src = `static/img/loading.gif`;
            mainTitle.setAttribute('data-filename', titles[0]);

            // 后台替换图片
            loadImageWhenReady(mainImg, `/currentfilepath/title_0.png`);

            // 设置选中的标题
            selectedTitle = titles[0];
        }

        // 获取并显示标题文字
        await fetchAndDisplayTitleText();

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
