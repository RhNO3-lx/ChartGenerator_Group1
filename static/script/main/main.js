function applyFontSettings() {
    const font = document.getElementById('fontSelector').value;
    const size = document.getElementById('fontSizeInput').value + 'px';
    document.querySelectorAll('.editable-text').forEach(el => {
        el.style.fontFamily = font;
        el.style.fontSize = size;
    });
}

document.getElementById('fontSelector').addEventListener('change', applyFontSettings);
document.getElementById('fontSizeInput').addEventListener('input', applyFontSettings);

// 使元素支持拖动 + 等比缩放
function enableInteract(el) {
    let isResizing = false;

    // 拖动逻辑
    interact('.resizable').draggable({
        listeners: {
            move(event) {
                if (isResizing) return;  // 若正在缩放，则不触发拖动
                const target = event.target;
                const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;
                target.style.transform = `translate(${x}px, ${y}px)`;
                target.setAttribute('data-x', x);
                target.setAttribute('data-y', y);
            }
        }
    });

    // 缩放逻辑
    let aspectRatio = 1;

    interact('.resizable').resizable({
        edges: { left: true, right: true, bottom: true, top: true },
        listeners: {
            start(event) {
                isResizing = true;
                event.target.classList.add('resizing');

                // 记录初始比例
                const rect = event.target.getBoundingClientRect();
                aspectRatio = rect.width / rect.height;
            },
            move(event) {
                const target = event.target;

                // 用 height 推出 width，保持等比
                const newHeight = event.rect.height;
                const newWidth = newHeight * aspectRatio;

                // 设置容器宽高
                target.style.width = `${newWidth}px`;
                target.style.height = `${newHeight}px`;

                // 同步 SVG 或图片的宽高
                const content = target.querySelector('svg, img');
                if (content) {
                    content.style.width = `${newWidth}px`;
                    content.style.height = `${newHeight}px`;

                    if (content.tagName.toLowerCase() === 'svg') {
                        content.setAttribute('width', newWidth);
                        content.setAttribute('height', newHeight);
                    }
                }
            },
            end(event) {
                isResizing = false;
                event.target.classList.remove('resizing');
            }
        }
    });

    el.addEventListener('mousedown', () => {
        document.querySelectorAll('.resizable').forEach(div => {
                div.classList.remove('selected');
        });
        el.classList.add('selected');
    });
}

// 插入图表或图片
function insertIntoCanvas(type, content, id) {
    const canvas = document.getElementById('canvas');
    const wrapper = document.createElement('div');
    wrapper.className = 'resizable';
    wrapper.setAttribute('id', id);
    // TODO 用layout控制位置
    wrapper.style.left = Math.random() * 200 + 'px';
    wrapper.style.top = Math.random() * 100 + 'px';
    wrapper.style.position = 'absolute'; // 确保定位正确
    wrapper.style.backgroundColor = 'transparent'; 

    if (type === 'svg') {
        wrapper.innerHTML = content;
        const maxSize = 1000; // 最大尺寸限制
        // 等待 SVG 渲染后获取其尺寸
        setTimeout(() => {
            const svg = wrapper.querySelector('svg');
            if (svg) {
                // 如果 SVG 有固定 width/height，使用它们
                const svgWidth = svg.width.baseVal.value || svg.clientWidth;
                const svgHeight = svg.height.baseVal.value || svg.clientHeight;
                
                const scale = Math.min(maxSize / svgWidth, maxSize / svgHeight, 1); // 计算缩放比例，不超过1
                wrapper.style.width = `${svgWidth * scale}px`;
                wrapper.style.height = `${svgHeight * scale}px`;
                svg.setAttribute('viewBox', `0 0 ${svgWidth * scale} ${svgHeight * scale}`);
                // console.info(svg)
            }
        }, 0);

    } else {
        const img = document.createElement('img');
        img.src = content;
        const maxSize = 300; // 最大尺寸限制
        img.onload = () => {
            // 图片加载完成后设置容器尺寸
            const scale = Math.min(maxSize / img.naturalWidth, maxSize / img.naturalHeight, 1); // 计算缩放比例，不超过1
            wrapper.style.width = `${img.naturalWidth * scale}px`;
            wrapper.style.height = `${img.naturalHeight * scale}px`;
            console.info(scale)
            console.info(maxSize / img.naturalWidth)
            console.info(maxSize / img.naturalHeight)
        };
        wrapper.appendChild(img);
    }

    canvas.appendChild(wrapper);
    enableInteract(wrapper); // 启用交互
}


function getTranslatedPosition(el) {
    const rect = el.getBoundingClientRect();
    const parentRect = el.offsetParent?.getBoundingClientRect() || { left: 0, top: 0 };

    // 计算相对 canvas 的偏移位置（包括 transform）
    return {
        x: rect.left - parentRect.left,
        y: rect.top - parentRect.top
    };
}


function loadIMG(chartType, data, title, pictogram) {
    if (!chartType || !data) {
        alert("请确保已选择数据源和图表类型");
        return;
    }

    const canvas = document.getElementById('canvas');
    canvas.innerHTML = `<div class="loading"><div class="loading-spinner"></div><span>正在加载图表...</span></div>`;

    const svgURL = `/authoring/chart?charttype=${encodeURIComponent(chartType)}&data=${encodeURIComponent(data)}&title=${encodeURIComponent(title)}&pictogram=${encodeURIComponent(pictogram)}`;

    fetch(svgURL)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();  // 👈 改为解析 JSON 响应
        })
        .then(response => {
            const { svg, img1, img2 } = response;

            canvas.innerHTML = '';
            insertIntoCanvas('svg', svg, 'svgChart');
            insertIntoCanvas('img', img1, 'img1');
            insertIntoCanvas('img', img2, 'img2');
        })
        .catch(err => {
            canvas.innerHTML = `<div class="error-message">加载图表失败: ${err.message}</div>`;
            console.error("加载图表失败:", err);
        });
}

function exportCanvasAsSVG() {
    const canvas = document.getElementById('canvas');
    const svgNS = "http://www.w3.org/2000/svg";
    const bg_color = "#f5f3ef"; // 设置背景颜色

    // 获取所有 resizable 元素的边界，用于确定 SVG 尺寸
    const resizables = canvas.querySelectorAll('.resizable');
    let maxRight = 0, maxBottom = 0;

    resizables.forEach(el => {
        const elRight = el.offsetLeft + el.offsetWidth;
        const elBottom = el.offsetTop + el.offsetHeight;
        if (elRight > maxRight) maxRight = elRight;
        if (elBottom > maxBottom) maxBottom = elBottom;
    });

    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("xmlns", svgNS);
    svg.setAttribute("width", maxRight);
    svg.setAttribute("height", maxBottom);
    svg.setAttribute("viewBox", `0 0 ${maxRight} ${maxBottom}`);

    // 添加背景矩形，填充 bg_color
    const backgroundRect = document.createElementNS(svgNS, "rect");
    backgroundRect.setAttribute("x", 0);
    backgroundRect.setAttribute("y", 0);
    backgroundRect.setAttribute("width", maxRight);
    backgroundRect.setAttribute("height", maxBottom);
    backgroundRect.setAttribute("fill", bg_color);  // 背景颜色
    svg.appendChild(backgroundRect);

    // 遍历每个元素并复制到 SVG 中
    resizables.forEach(el => {
        const { x: offsetX, y: offsetY } = getTranslatedPosition(el);

        const svgInner = el.querySelector('svg');
        if (svgInner) {
            const clone = svgInner.cloneNode(true);
            const wrapper = document.createElementNS(svgNS, "g");
            wrapper.setAttribute("transform", `translate(${offsetX}, ${offsetY})`);
            wrapper.appendChild(clone);
            svg.appendChild(wrapper);
        }

        const img = el.querySelector('img');
        if (img) {
            const imageEl = document.createElementNS(svgNS, "image");
            imageEl.setAttributeNS(null, 'href', img.src);
            imageEl.setAttribute('x', offsetX);
            imageEl.setAttribute('y', offsetY);
            imageEl.setAttribute('width', el.offsetWidth);
            imageEl.setAttribute('height', el.offsetHeight);
            svg.appendChild(imageEl);
        }

        // 更新最大宽高（用于 SVG 尺寸）
        const right = offsetX + el.offsetWidth;
        const bottom = offsetY + el.offsetHeight;
        if (right > maxRight) maxRight = right;
        if (bottom > maxBottom) maxBottom = bottom;
    });

    // 导出逻辑
    const serializer = new XMLSerializer();
    const svgStr = serializer.serializeToString(svg);
    const blob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "infographic.svg";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}


// 初始化加载
window.addEventListener('DOMContentLoaded', () => {
    const initialChartType = "{{ charttype | safe }}";
    const initialData = "{{ data | safe }}";
    const initialTitle = "{{ title | safe }}";
    const initialPictogram= "{{ pictogram | safe }}";
    if (initialChartType && initialData) {
        loadIMG(initialChartType, initialData, initialTitle, initialPictogram);
    }
});
