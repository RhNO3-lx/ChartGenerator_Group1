// 查找参考图
// async function findReferenceImages() {
//     if (!currentDataFile) {
//         alert('请先选择一个数据集');
//         return;
//     }
    

//     // 显示加载overlay
//     document.getElementById('loadingOverlay').style.display = 'flex';
//     document.getElementById('loadingText').textContent = '查找参考信息图表...';
//     document.getElementById('nextStepBtn').disabled = true;

//     // 模拟查找过程（1.5秒）
//     setTimeout(() => {
//         showReferenceImages();
//         hideLoading();
//         document.getElementById('nextStepBtn').disabled = false;
//     }, 1500);


    
// }

// 查找参考图
async function findReferenceImages() {
    if (!currentDataFile) {
        alert('请先选择一个数据集');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('loadingText').textContent = "查找参考信息图表..."
    document.getElementById('selectReferenceBtn').disabled = true;

    try {
        // 开始查找
        const response = await fetch(`/api/start_find_reference/${currentDataFile}`);
        const result = await response.json();
        
        if (result.status === 'started') {
            // 轮询状态直到完成
            setTimeout(() => {
                showReferenceImages();
                hideLoading();
                document.getElementById('nextStepBtn').disabled = false;
            }, 1500);
        }
        
    } catch (error) {
        console.error('参考图查找失败:', error);
        alert('参考图查找失败，请重试');
        hideLoading();
    }
}

// 显示参考图
async function showReferenceImages() {
    try {
        // 获取随机参考图
        const response = await fetch('/api/references');
        const result = await response.json();
        const mainImage = result.main_image;
        const randomImages = result.random_images || [];

        // 设置主参考图（随机选择的第一张作为推荐）
        const mainRef = document.getElementById('mainReference');
        const mainImg = mainRef.querySelector('.reference-image');

        if (mainImage) {
            mainImg.src = `/infographics/${mainImage}`;
            mainRef.setAttribute('data-filename', mainImage);
        }

        // 设置其他四个参考图
        for (let i = 0; i < 4; i++) {
            const otherRef = document.getElementById(`otherRef${i + 1}`);
            const otherImg = otherRef.querySelector('.reference-image');
            if (randomImages[i]) {
                otherImg.src = `/infographics/${randomImages[i]}`;
                otherRef.setAttribute('data-filename', randomImages[i]);
            }
        }

        // 添加点击事件
        setupReferenceSelection();

        // 显示参考图卡片
        const referenceCard = document.getElementById('referenceCard');
        referenceCard.classList.remove('hidden');
        referenceCard.classList.add('fade-in');
        referenceCard.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('获取参考图失败:', error);
        alert('获取参考图失败，请重试');
    }
}

// 设置参考图选择
function setupReferenceSelection() {
    const referenceItems = document.querySelectorAll('.reference-item');
    const selectBtn = document.getElementById('selectReferenceBtn');
    
    referenceItems.forEach(item => {
        item.addEventListener('click', function() {
            // 移除所有选中状态
            referenceItems.forEach(ref => ref.classList.remove('selected'));
            
            // 检查选择是否改变
            if (selectedReference != this.getAttribute('data-filename') && selectedReference){
                console.log("changed");
                hideCards(["variationCard", "titleCard", "pictogramCard", "resultCard"])
                
            }
            
            // 添加选中状态
            this.classList.add('selected');
            selectedReference = this.getAttribute('data-filename');
            
            // 检查是否选择了最佳匹配
            // const baseFileName = currentDataFile.replace('.csv', '');
            // const isCorrectChoice = selectedReference === `${baseFileName}-Origin`;
            
            selectBtn.disabled = false;
        });
    });
}
