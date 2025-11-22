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
        else if (status.step === 'pictogram_generation' && status.completed) {
            // 布局抽取完成，显示标题选择
            setTimeout(() => {
                showPictogramSelection();
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