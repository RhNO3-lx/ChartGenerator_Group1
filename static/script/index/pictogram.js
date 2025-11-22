

// 开始配图生成
async function startPictogramGeneration() {
    if (!selectedTitle) {
        alert('请先选择一个标题');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectTitleBtn').disabled = true;

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

// 显示配图选择
async function showPictogramSelection() {
    try {
        const response = await fetch(`/api/pictograms`);
        const pictograms = await response.json();
        
        // 设置最佳匹配配图
        if (pictograms) {
            const mainPictogram = document.getElementById('mainPictogram');
            const mainImg = mainPictogram.querySelector('.selection-image');
            mainImg.src = `static/img/loading.gif`;
            mainPictogram.setAttribute('data-filename', pictograms[0]);
            mainPictogram.setAttribute('data-type', 'origin');
            mainPictogram.setAttribute('data-index', '0'); // 主标题索引为0
            
            // 后台替换主图
            loadImageWhenReady(mainImg, `/currentfilepath/pictogram_0.png`);
        
            // 设置生成的配图选项
            for (let i = 1; i < 5; i++) {
                const pictogramOption = document.getElementById(`pictogramOption${i}`);
                console.log(pictogramOption)
                const pictogramImg = pictogramOption.querySelector('.selection-image');
                
                if (pictograms[i]) {
                    pictogramImg.src = `static/img/loading.gif`;
                    pictogramOption.setAttribute('data-filename', pictograms[i]);
                    pictogramOption.setAttribute('data-type', 'generated');
                    pictogramOption.setAttribute('data-index', String(i));

                    // 后台替换选项图
                    loadImageWhenReady(pictogramImg, `/currentfilepath/pictogram_${i}.png`);
                }
            }
        }
        
        // 设置配图选择事件
        setupPictogramSelection();
        
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

// 设置配图选择
function setupPictogramSelection() {
    const pictogramItems = document.querySelectorAll('#pictogramCard .selection-item');
    const selectBtn = document.getElementById('selectPictogramBtn');
    
    pictogramItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            pictogramItems.forEach(pictogram => pictogram.classList.remove('selected'));
            
            // 添加选中状态
            this.classList.add('selected');
            selectedPictogram = this.getAttribute('data-filename');
            
            // 只有选择最佳匹配（左边的图片）才能进入下一步
            const isMainPictogram = this.id === 'mainPictogram';
            selectBtn.disabled = !isMainPictogram;
        });
    });
}
