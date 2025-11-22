// Improved version with better error handling and image loading

// Start layout extraction
async function startLayoutExtraction() {
    if (!selectedReference) {
        alert('请先选择一个参考图表');
        return;
    }

    // Show loading overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectReferenceBtn').disabled = true;

    try {
        const response = await fetch(`/api/start_layout_extraction/${selectedReference}/${currentDataFile}`);
        const result = await response.json();
        
        if (result.status === 'started') {
            checkStatus();
        }
        
    } catch (error) {
        console.error('布局抽取失败:', error);
        alert('布局抽取失败，请重试');
        hideLoading();
    }
}


async function showVariationSelection() {
    try {
        const response = await fetch(`/api/variation/selection`);
        const variations_selection = await response.json();
        console.info(variations_selection);

        if (variations_selection) {
            // 主图处理
            const mainVariation = document.getElementById('mainVariation');
            const mainImg = mainVariation.querySelector('.selection-image');
            mainImg.src = `static/img/loading.gif`;
            mainImg.alt = `${variations_selection[0]}`;
            mainVariation.setAttribute('data-filename', variations_selection[0]);
            mainVariation.setAttribute('data-type', 'origin');
            mainVariation.setAttribute('data-index', '0');

            // 后台替换主图
            loadImageWhenReady(mainImg, `/currentfilepath/${variations_selection[0]}.svg`);

            // 选项图处理
            for (let i = 1; i < 5; i++) {
                const variationOption = document.getElementById(`variationOption${i}`);
                const variationImg = variationOption.querySelector('.selection-image');
                variationOption.style.display = 'block';

                if (variations_selection[i]) {
                    variationImg.src = `static/img/loading.gif`;
                    variationImg.alt = `${variations_selection[i]}`;
                    variationOption.setAttribute('data-filename', variations_selection[i]);
                    variationOption.setAttribute('data-type', 'generated');
                    variationOption.setAttribute('data-index', String(i));

                    // 后台替换选项图
                    loadImageWhenReady(variationImg, `/currentfilepath/${variations_selection[i]}.svg`);
                }
            }
        }

        // 设置标题选择事件
        setupVariationSelection();

        // 显示标题卡片
        const variationCard = document.getElementById('variationCard');
        variationCard.classList.remove('hidden');
        variationCard.classList.add('fade-in');
        variationCard.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('获取图表失败:', error);
        alert('获取图表失败，请重试');
    }
}


// Setup variation selection (unchanged)
function setupVariationSelection() {
    const variationItems = document.querySelectorAll('#variationCard .selection-item');
    const selectBtn = document.getElementById('selectVariationBtn');
    
    variationItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            variationItems.forEach(variation => variation.classList.remove('selected'));
            
            // 添加选中状态
            this.classList.add('selected');
            selectedVariation = this.getAttribute('data-filename');
            selectedVariationIndex = parseInt(this.getAttribute('data-index')) || 0;
            selectBtn.disabled = false;
        });
    });
}

