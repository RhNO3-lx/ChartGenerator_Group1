

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

// 显示配图选择（3选1版本）
async function showPictogramSelection() {
    try {
        const response = await fetch(`/api/status`);
        const status = await response.json();

        const pictogramOptions = status.pictogram_options || {};
        const pictogramKeys = Object.keys(pictogramOptions);

        if (pictogramKeys.length > 0) {
            const container = document.getElementById('pictogramContainer');
            container.innerHTML = '';

            // 创建3个配图选项
            for (let i = 0; i < 3; i++) {
                const pictogramKey = `pictogram_${i}.png`;
                const pictogramData = pictogramOptions[pictogramKey];

                if (pictogramData && pictogramData.success) {
                    const item = document.createElement('div');
                    item.className = 'pictogram-item';
                    item.setAttribute('data-filename', pictogramKey);

                    item.innerHTML = `
                        <div class="pictogram-image-container">
                            <img class="pictogram-image" src="/currentfilepath/${pictogramKey}?t=${Date.now()}" alt="配图 ${i+1}">
                        </div>
                    `;

                    container.appendChild(item);
                }
            }

            // 设置点击事件
            setupPictogramSelection();
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

// 设置配图选择事件
function setupPictogramSelection() {
    const pictogramItems = document.querySelectorAll('.pictogram-item');
    const selectBtn = document.getElementById('selectPictogramBtn');

    pictogramItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            pictogramItems.forEach(p => p.classList.remove('selected'));

            // 检查选择是否改变
            if (selectedPictogram != this.getAttribute('data-filename') && selectedPictogram) {
                hideCards(["resultCard"]);
            }

            // 添加选中状态
            this.classList.add('selected');
            selectedPictogram = this.getAttribute('data-filename');

            selectBtn.disabled = false;
        });
    });
}
