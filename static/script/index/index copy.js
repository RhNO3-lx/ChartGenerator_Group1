let currentDataFile = '';
let selectedReference = '';
let selectedVariation = '';
let selectedTitle = '';
let selectedTitleIndex = 0;
let selectedPictogram = '';

// 数据选择变化事件
document.getElementById('dataSelect').addEventListener('change', function() {
    const selectedFile = this.value;
    if (selectedFile) {
        loadData(selectedFile);
        currentDataFile = selectedFile;
    } else {
        hideAllCards();
    }
});

// 隐藏所有卡片
function hideAllCards() {
    document.getElementById('dataPreview').classList.add('hidden');
    document.getElementById('referenceCard').classList.add('hidden');
    document.getElementById('variationCard').classList.add('hidden');
    document.getElementById('titleCard').classList.add('hidden');
    document.getElementById('pictogramCard').classList.add('hidden');
    document.getElementById('resultCard').classList.add('hidden');
    
    // 重置选择状态
    selectedReference = '';
    selectedVariation = '';
    selectedTitle = '';
    selectedTitleIndex = 0;
    selectedPictogram = '';
}

function hideCards(cards) {
    cards.forEach(card => {
        const element = document.getElementById(card);
        if (element) {  // 检查元素是否存在
            element.classList.add('hidden');
            console.info(`hide "${card}"`);
        } else {
            console.info(`Element with ID "${card}" not found.`);
        }
    });

    // 重置选择状态

    // selectedReference = '';
    // selectedVariation = '';
    // selectedTitle = '';
    // selectedTitleIndex = 0;
    // selectedPictogram = '';
}

// 加载数据
async function loadData(filename) {
    try {
        const response = await fetch(`/api/data/${filename}`);
        const result = await response.json();
        
        if (result.columns && result.data) {
            displayTable(result.columns, result.data);
            document.getElementById('dataPreview').classList.remove('hidden');
            document.getElementById('referenceCard').classList.add('hidden');
            document.getElementById('variationCard').classList.add('hidden');
            document.getElementById('titleCard').classList.add('hidden');
            document.getElementById('pictogramCard').classList.add('hidden');
            document.getElementById('resultCard').classList.add('hidden');
        }
    } catch (error) {
        console.error('加载数据失败:', error);
        alert('加载数据失败，请重试');
    }
}

// 显示表格
function displayTable(columns, data) {
    const tableHeader = document.getElementById('tableHeader');
    const tableBody = document.getElementById('tableBody');
    
    // 清空现有内容
    tableHeader.innerHTML = '';
    tableBody.innerHTML = '';
    
    // 创建表头
    const headerRow = document.createElement('tr');
    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });
    tableHeader.appendChild(headerRow);
    
    // 创建表格行
    data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            td.textContent = row[column] || '';
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

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
    const baseFileName = currentDataFile.replace('.csv', '');
    
    try {
        // 获取随机参考图
        const response = await fetch('/api/references');
        const result = await response.json();
        const randomImages = result.random_images || [];
        
        // 设置主参考图（对应的Origin图）
        const mainRef = document.getElementById('mainReference');
        const mainImg = mainRef.querySelector('.reference-image');
        
        // 尝试PNG和JPG格式
        let mainImageSrc = `/infographics/${baseFileName}-Origin.png`;
        mainImg.src = mainImageSrc;
        mainRef.setAttribute('data-filename', `${baseFileName}-Origin.png`);
        mainImg.onerror = function() {
            this.src = `/infographics/${baseFileName}-Origin.jpg`;
            mainRef.setAttribute('data-filename', `${baseFileName}-Origin.jpg`);
        };
        
        // 设置其他四个参考图（来自other_infographics的随机图片）
        for (let i = 0; i < 4; i++) {
            const otherRef = document.getElementById(`otherRef${i + 1}`);
            const otherImg = otherRef.querySelector('.reference-image');
            if (randomImages[i]) {
                otherImg.src = `/other_infographics/${randomImages[i]}`;
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

// 开始布局抽取
async function startLayoutExtraction() {
    if (!selectedReference) {
        alert('请先选择一个参考图表');
        return;
    }

    // 显示加载overlay
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('selectReferenceBtn').disabled = true;

    try {
        // 开始布局抽取
        const response = await fetch(`/api/start_layout_extraction/${selectedReference}/${currentDataFile}`);
        const result = await response.json();
        
        if (result.status === 'started') {
            // 轮询状态直到完成
            checkStatus();
        }
        
    } catch (error) {
        console.error('布局抽取失败:', error);
        alert('布局抽取失败，请重试');
        hideLoading();
    }
}

// 检查布局抽取状态
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        document.getElementById('loadingText').textContent = status.progress || '处理中...';
        
        if (status.step === 'layout_extraction' && status.completed) {
            // 布局抽取完成，显示标题选择
            setTimeout(() => {
                showVariationSelection();
                hideLoading();
            }, 500);
        } 
        else if (status.step === 'title_generation' && status.completed) {
            // 布局抽取完成，显示标题选择
            setTimeout(() => {
                showTitleSelection();
                hideLoading();
            }, 500);
        } 
        else if (status.status === 'processing') {
            // 继续轮询
            setTimeout(checkStatus, 500);
        } else {
            hideLoading();
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        hideLoading();
    }
}

// 显示类型选择
async function showVariationSelection() {
    try {
        const response = await fetch(`/api/variation/selection`);
        const variations_selection = await response.json();
        
        
        // 设置最佳匹配类型
        if (variations_selection) {
            const mainVariation = document.getElementById('mainVariation');
            const mainImg = mainVariation.querySelector('.selection-image');
            mainImg.src = `/origin_images/titles/${variations_selection[0]}`;
            mainImg.alt = `${variations_selection[0]}`;
            mainVariation.setAttribute('data-filename', variations_selection[0]);
            mainVariation.setAttribute('data-type', 'origin');
            mainVariation.setAttribute('data-index', '0'); // 主标题索引为0（对应Art.png）
        
        
            // 设置生成的标题选项
            for (let i = 1; i < 5; i++) {
                const variationOption = document.getElementById(`variationOption${i}`);
                const variationImg = variationOption.querySelector('.selection-image');
                variationOption.style.display = 'block'; // 确保显示
                if (variations_selection && variations_selection[i]) {
                    variationImg.src = `/generated_images/titles/${variations_selection[i]}`;
                    variationImg.alt = `${variations_selection[i]}`;
                    variationOption.setAttribute('data-filename', variations_selection[i]);
                    variationOption.setAttribute('data-type', 'generated');
                    variationOption.setAttribute('data-index', String(i)); // 选项索引为1,2,3,4（对应Art-Title1.png到Art-Title4.png）
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
        console.error('获取标题失败:', error);
        alert('获取标题失败，请重试');
    }
}

// 设置类型选择
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
        console.error('布局抽取失败:', error);
        alert('布局抽取失败，请重试');
        hideLoading();
    }
}

// 显示标题选择
async function showTitleSelection() {
    try {
        const response = await fetch(`/api/titles`);
        const titles = await response.json();
        
        // 设置最佳匹配标题
        if (titles) {
            const mainTitle = document.getElementById('mainTitle');
            const mainImg = mainTitle.querySelector('.selection-image');
            mainImg.src = `/currentfilepath/${titles[0]}`;
            mainTitle.setAttribute('data-filename', titles[0]);
            mainTitle.setAttribute('data-type', 'origin');
            mainTitle.setAttribute('data-index', '0'); // 主标题索引为0
        
        
            // 设置生成的标题选项
            for (let i = 1; i < 5; i++) {
                const titleOption = document.getElementById(`titleOption${i}`);
                const titleImg = titleOption.querySelector('.selection-image');
                titleOption.style.display = 'block'; // 确保显示
                if (titles && titles[i]) {
                    titleImg.src = `/currentfilepath/${titles[i]}`;
                    titleOption.setAttribute('data-filename', titles[i]);
                    titleOption.setAttribute('data-type', 'generated');
                    titleOption.setAttribute('data-index', String(i)); // 选项索引为1,2,3,4（对应Art-Title1.png到Art-Title4.png）
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
        const response = await fetch('/api/start_pictogram_generation');
        const result = await response.json();
        
        if (result.status === 'started') {
            // 轮询状态直到完成
            checkPictogramGenerationStatus();
        }
        
    } catch (error) {
        console.error('配图生成失败:', error);
        alert('配图生成失败，请重试');
        hideLoading();
    }
}

// 检查配图生成状态
async function checkPictogramGenerationStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        document.getElementById('loadingText').textContent = status.progress || '处理中...';
        
        if (status.step === 'pictogram_selection' && status.completed) {
            // 配图生成完成，显示配图选择
            setTimeout(() => {
                showPictogramSelection();
                hideLoading();
            }, 500);
        } else if (status.status === 'processing') {
            // 继续轮询
            setTimeout(checkPictogramGenerationStatus, 500);
        } else {
            hideLoading();
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        hideLoading();
    }
}

// 显示配图选择
async function showPictogramSelection() {
    try {
        const response = await fetch(`/api/pictograms/${currentDataFile}`);
        const pictograms = await response.json();
        
        // 设置最佳匹配配图
        if (pictograms.origin) {
            const mainPictogram = document.getElementById('mainPictogram');
            const mainImg = mainPictogram.querySelector('.selection-image');
            mainImg.src = `/origin_images/pictograms/${pictograms.origin}`;
            mainPictogram.setAttribute('data-filename', pictograms.origin);
            mainPictogram.setAttribute('data-type', 'origin');
        }
        
        // 设置生成的配图选项
        for (let i = 0; i < 4; i++) {
            const pictogramOption = document.getElementById(`pictogramOption${i + 1}`);
            const pictogramImg = pictogramOption.querySelector('.selection-image');
            if (pictograms.generated[i]) {
                pictogramImg.src = `/generated_images/pictograms/${pictograms.generated[i]}`;
                pictogramOption.setAttribute('data-filename', pictograms.generated[i]);
                pictogramOption.setAttribute('data-type', 'generated');
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

// 生成最终信息图表
async function generateFinalInfographic() {
    if (!selectedPictogram) {
        alert('请先选择一个配图');
        return;
    }

    const charttype = selectedVariation;
    const data = currentDataFile.replace('.csv', '');;
    
    if (!charttype || !data) {
        alert('请先选择数据和图表类型');
        return;
    }
    
    // 跳转到 ChartGalaxy 主页面，并且带上 charttype 和 data 参数
    // 假设那个页面叫 index.html，如果部署在根路径就直接写 /index.html
    const url = `/authoring/generate_final?charttype=${charttype}&data=${data}&title=${selectedTitle}&pictogram=${selectedPictogram}`
    window.location.href = url;
    // 显示加载overlay
    // document.getElementById('loadingOverlay').style.display = 'flex';
    // document.getElementById('selectPictogramBtn').disabled = true;

    // try {
    //     // 构建请求URL，对于Art演示需要传递选择的标题索引
    //     let apiUrl = `/api/generate_final/${currentDataFile}`;
    //     if (isArtDemo && selectedTitleIndex) {
    //         apiUrl += `?selected_title_index=${selectedTitleIndex}`;
    //     }
        
    //     // 开始最终生成
    //     const response = await fetch(apiUrl);
    //     const result = await response.json();
        
    //     if (result.error) {
    //         alert(result.error);
    //         return;
    //     }

    //     // 轮询状态
    //     checkFinalGenerationStatus();
        
    // } catch (error) {
    //     console.error('最终生成失败:', error);
    //     alert('最终生成失败，请重试');
    //     hideLoading();
    // }
}

// 检查最终生成状态
async function checkFinalGenerationStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        document.getElementById('loadingText').textContent = status.progress || '处理中...';
        
        if (status.step === 'final_result' && status.completed && status.image_name) {
            // 最终生成完成
            setTimeout(() => {
                showResult(status.image_name);
                hideLoading();
            }, 500);
        } else if (status.status === 'processing') {
            // 继续轮询
            setTimeout(checkFinalGenerationStatus, 500);
        } else {
            hideLoading();
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        hideLoading();
    }
}

// 显示结果
function showResult(imageName) {
    const resultImage = document.getElementById('resultImage');
    resultImage.src = `/infographics/${imageName}`;
    
    const resultCard = document.getElementById('resultCard');
    resultCard.classList.remove('hidden');
    resultCard.classList.add('fade-in');
    
    // 滚动到结果
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

// 隐藏加载界面
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}
