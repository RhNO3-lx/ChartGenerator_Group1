

// 开始配图生成
async function startPictogramGeneration() {
    if (!selectedTitle) {
        alert('请先确认标题');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectPictogramBtn').disabled = true;
    document.getElementById('regeneratePictogramBtn').disabled = true;

    try {
        // 开始配图生成
        const response = await fetch(`/api/start_pictogram_generation/${selectedTitle}`);
        const result = await response.json();

        if (result.status === 'started') {
            // 轮询状态直到完成
            checkStatus();
        }

    } catch (error) {
        console.error('配图生成失败:', error);
        alert('配图生成失败，请重试');
        hideLoading();
    }
}

// 重新生成配图
async function regeneratePictogram() {
    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectPictogramBtn').disabled = true;
    document.getElementById('regeneratePictogramBtn').disabled = true;

    try {
        // 调用重新生成API
        const response = await fetch(`/api/regenerate_pictogram/${selectedTitle}`);
        const result = await response.json();

        if (result.status === 'started') {
            // 轮询状态直到完成
            checkStatus();
        }

    } catch (error) {
        console.error('重新生成配图失败:', error);
        alert('重新生成配图失败，请重试');
        hideLoading();
    }
}

// 显示配图选择（单张显示版本）
async function showPictogramSelection() {
    try {
        const response = await fetch(`/api/pictograms`);
        const pictograms = await response.json();

        if (pictograms && pictograms.length > 0) {
            // 单张图片显示
            const mainPictogram = document.getElementById('mainPictogram');
            const mainImg = mainPictogram.querySelector('.selection-image');
            mainImg.src = `static/img/loading.gif`;
            mainPictogram.setAttribute('data-filename', pictograms[0]);

            // 后台替换图片
            loadImageWhenReady(mainImg, `/currentfilepath/pictogram_0.png`);

            // 设置选中的配图
            selectedPictogram = pictograms[0];
        }

        // 启用按钮
        document.getElementById('selectPictogramBtn').disabled = false;
        document.getElementById('regeneratePictogramBtn').disabled = false;

        // 显示配图卡片
        const pictogramCard = document.getElementById('pictogramCard');
        pictogramCard.classList.remove('hidden');
        pictogramCard.classList.add('fade-in');
        pictogramCard.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('获取配图失败:', error);
        alert('获取配图失败，请重试');
    }
}
